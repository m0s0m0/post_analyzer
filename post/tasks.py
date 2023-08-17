import time

from celery import shared_task, Task, group, chord
from post_analyzer.celery import app

from .models import Post


class BaseTask(Task):
    max_retries = 3
    retry_delay = 2 
    time_limit = 15

def find_text_split(text, max_length):
    # Find the last space within max_length characters
    split_point = max_length
    while split_point > 0 and not text[split_point].isspace():
        split_point -= 1
    return split_point

@app.task(base=BaseTask)
def analyze_partial_text(text, start, end, **kwargs):
    try:
        total_words = 0
        total_word_length = 0
        word_start = None

        for i, char in enumerate(text[start:end]):
            if char.isalpha():
                if word_start is None:
                    word_start = i
            elif word_start is not None:
                total_words += 1
                total_word_length += i - word_start
                word_start = None

        if word_start is not None:
            total_words += 1
            total_word_length += len(text[start:end]) - word_start

        return {
            "total_words": total_words,
            "total_word_length": total_word_length
        }
    except Exception as e:
        return {'error': str(e)}


@app.task(base=BaseTask)
def analyze_post(post_id, **kwargs):
    try:

        post_content = Post.objects.get(uuid=post_id)
        text = post_content.post_description
        max_chunk_length = len(text) // 2
        split_point = find_text_split(text, max_chunk_length)
        chunk1 = text[:split_point]
        chunk2 = text[split_point:]

        task1 = analyze_partial_text.si(chunk1, 0, len(chunk1))
        task2 = analyze_partial_text.si(chunk2, 0, len(chunk2))

        result_group = group([task1, task2])
        result_chain = chord(result_group)(process_results.s(post_id))

        return {'result_chain_id': result_chain.id}

    except Post.DoesNotExist:
        return {'error': f"Post with ID {post_id} does not exist."}
    except Exception as e:
        if analyze_post.request.retries >= analyze_post.max_retries:
            return {'error': str(e)}

        raise analyze_post.retry(exc=e)


@app.task(base=BaseTask)
def process_results(subtask_results, **kwargs):
    try:
        total_words = 0
        total_word_length = 0

        for result in subtask_results:
            total_words += result.get('total_words', 0)
            total_word_length += result.get('total_word_length', 0)

        average_word_length = total_word_length / total_words if total_words > 0 else 0


        update_post_model.delay(post_id, total_words, average_word_length)


        return {
            "total_words": total_words,
            "average_word_length": average_word_length
        }
    except Exception as e:
        return {'error': str(e)}


@app.task(base=BaseTask)
def update_post_model(post_id, total_words, average_word_length):
    try:
        post = Post.objects.get(uuid=post_id)
        post.is_analysed = True
        post.analysed_at = datetime.datetime.now()
        post.analysis_result = dict(total_words=total_words, average_word_length=average_word_length)
        post.save()
        return f'post id {post_id} updated with total words {total_words} and average_word_length{average_word_length}'
    except Post.DoesNotExist:
        return f'{post_id} update failed with total words {total_words} and average_word_length{average_word_length} as post_id dont exist'# Handle the case where the post no longer exist
    except (IntegrityError, DataError, ValidationError) as e:
        return f'{post_id} update failed with total words {total_words} and average_word_length{average_word_length} as {str(e.message)}'# Handle the case where the post no longer exist
