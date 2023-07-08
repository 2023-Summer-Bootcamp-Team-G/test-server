import requests

# 문장 저장 API 테스트
def test_save_sentence():
    url = "http://localhost:8000/sentences"
    payload = {"sentence": "Hello, World!"}
    response = requests.post(url, json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Sentence saved successfully"}

# 문장 리스트 조회 API 테스트
def test_get_sentences():
    url = "http://localhost:8000/sentences"
    response = requests.get(url)
    assert response.status_code == 200
    assert "sentences" in response.json()

    print(response.json())

# test_get_sentences() # 빈 리스트 문제 발생?
test_save_sentence()
test_get_sentences()
