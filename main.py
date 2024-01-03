from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import List

import numpy as np
import cv2
from starlette.status import HTTP_413_REQUEST_ENTITY_TOO_LARGE

app = FastAPI()

dog_cascade = cv2.CascadeClassifier('model/dog_face.xml')
cat_cascade = cv2.CascadeClassifier('model/haarcascade_frontalcatface_extended.xml')


@app.post("/detectDogFace")
def detect_dog_face_endpoint(files: List[UploadFile] = File(...)):
    results = []

    for file in files:
        validate_file_size(file)
        contents = file.read()

        is_dog_face_detected = detect_dog_face(contents)
        results.append(is_dog_face_detected)

    return {"results": results}


def detect_dog_face(contents):
    # 이미지를 NumPy 배열로 변환
    img = np.asarray(bytearray(contents), dtype="uint8")
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)

    # 그레이 스케일 변환
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 강아지 얼굴 감지
    dogs = dog_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
    cats = cat_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    # 감지된 얼굴이 있는지 여부를 반환

    return (len(dogs) + len(cats)) > 0

def validate_file_size(file: UploadFile):
    real = 0
    for chunk in file.file:
        real = real + len(chunk)
        if real > 2 * 1024 * 1024:
            raise HTTPException(
                status_code=HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Image size is too large"
            )