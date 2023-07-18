import requests


# 문장 저장 API 테스트
def test_save_sentence():
    url = "http://127.0.0.1:8000/sentences"
    payload = {"sentence": "API_test"}
    response = requests.post(url, json=payload)
    assert response.status_code == 200
    print(response.json())


# 문장 리스트 조회 API 테스트
def test_get_sentences():
    url = "http://127.0.0.1:8000/sentences"
    response = requests.get(url)
    assert response.status_code == 200
    # assert "sentences" in response.json()
    print(response.json())


test_get_sentences()
# test_save_sentence()
