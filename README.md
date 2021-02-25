# workInOut

## 필요사항
* [Python 3](https://www.python.org/downloads/)

## 필요한 패키지 설치
```dos
> pip install -r requirements.txt
```
## config/info.yml 수정
* ID, PWD 수정

## 실행 파일 생성
* dist 폴더에 실행파일 생성

맥OS
```bash
$ pyinstaller -F --add-data "config/info.yml:config" main.py  
```

윈도우
```bash
$ pyinstaller -F --add-data "config/info.yml;config" main.py
```
