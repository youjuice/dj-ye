import nltk
import os


def download_nltk_data():
    # NLTK 데이터를 저장할 디렉토리 설정
    # 현재 스크립트가 있는 디렉토리에 'nltk_data' 폴더를 만듭니다.
    nltk_data_dir = os.path.join(os.path.dirname(__file__), 'nltk_data')

    if not os.path.exists(nltk_data_dir):
        os.makedirs(nltk_data_dir)

    # NLTK 데이터 경로 설정
    nltk.data.path.append(nltk_data_dir)

    # 필요한 NLTK 데이터 다운로드
    resources = ['punkt', 'stopwords', 'wordnet']
    for resource in resources:
        print(f"Downloading {resource}...")
        nltk.download(resource, download_dir=nltk_data_dir, quiet=True)
        print(f"{resource} downloaded successfully.")


if __name__ == "__main__":
    print("Starting NLTK data download...")
    download_nltk_data()
    print("NLTK data download completed.")