"""
Benchmark tests for measuring performance of critical components.
"""
import json
import random
import string

import pytest


def generate_random_string(length=10):
    """Generate a random string of fixed length."""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))


def generate_mock_interview_data(num_questions=5):
    """Generate mock interview data for benchmarking."""
    questions = []
    for _ in range(num_questions):
        question = {
            "id": generate_random_string(8),
            "text": f"Tell me about {generate_random_string(5)}?",
            "type": random.choice(["behavioral", "technical", "situational"]),
            "difficulty": random.choice(["easy", "medium", "hard"]),
            "keywords": [generate_random_string(4) for _ in range(3)]
        }
        questions.append(question)
    
    return {
        "interview_id": generate_random_string(12),
        "candidate_id": generate_random_string(10),
        "job_title": f"{generate_random_string(7)} Engineer",
        "questions": questions,
        "duration_minutes": random.randint(30, 60),
        "settings": {
            "feedback_level": random.choice(["basic", "detailed", "expert"]),
            "recording_enabled": random.choice([True, False]),
            "transcript_enabled": True
        }
    }


def process_interview_data(data):
    """Simulate processing interview data."""
    # Simulate some processing work
    processed = {
        "id": data["interview_id"],
        "summary": f"Interview for {data['job_title']} position",
        "questions_count": len(data["questions"]),
        "processed_questions": []
    }
    
    for q in data["questions"]:
        # Process each question
        processed_q = {
            "id": q["id"],
            "text": q["text"],
            "analyzed_keywords": [k.upper() for k in q["keywords"]],
            "complexity_score": random.random() * 10,
            "clarity_score": random.random() * 10
        }
        processed["processed_questions"].append(processed_q)
    
    # Convert to JSON string and back to simulate serialization
    json_data = json.dumps(processed)
    result = json.loads(json_data)
    
    return result


@pytest.mark.benchmark(
    group="processing",
    min_time=0.1,
    max_time=0.5,
    min_rounds=5,
    timer=lambda: 0,
    disable_gc=True,
    warmup=False
)
def test_interview_data_processing(benchmark):
    """Benchmark the processing of interview data."""
    # Generate test data outside the benchmark
    data = generate_mock_interview_data(10)
    
    # Benchmark the processing function
    result = benchmark(process_interview_data, data)
    
    # Verify the result is correct
    assert result["id"] == data["interview_id"]
    assert result["questions_count"] == len(data["questions"])
    assert len(result["processed_questions"]) == len(data["questions"])


@pytest.mark.benchmark(
    group="data-generation",
    min_time=0.1,
    max_time=0.5,
    min_rounds=5,
    timer=lambda: 0,
    disable_gc=True,
    warmup=False
)
def test_data_generation_performance(benchmark):
    """Benchmark the generation of mock interview data."""
    # Benchmark the data generation function
    result = benchmark(generate_mock_interview_data, 20)
    
    # Verify the result is correct
    assert len(result["questions"]) == 20
    assert "interview_id" in result
    assert "candidate_id" in result


# Create parametrized benchmark test to compare different sizes
@pytest.mark.parametrize("num_questions", [5, 10, 20, 50, 100])
def test_processing_scaling(benchmark, num_questions):
    """Test how processing scales with the number of questions."""
    # Generate test data outside the benchmark
    data = generate_mock_interview_data(num_questions)
    
    # Benchmark the processing function
    result = benchmark(process_interview_data, data)
    
    # Verify the result is correct
    assert result["questions_count"] == num_questions 