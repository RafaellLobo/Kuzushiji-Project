import cv2
import matplotlib.pyplot as plt
from app.services.classifier import ClassificationService

classifier = ClassificationService(confidence_threshold=0.0)

img = cv2.imread("tests/teste_kmnist.png", cv2.IMREAD_GRAYSCALE)

if img is None:
    raise FileNotFoundError("Imagem não encontrada")

img = cv2.resize(img, (28, 28))

plt.imshow(img, cmap="gray")
plt.title("Imagem enviada ao classificador")
plt.show()

print("normal:", classifier.debug_predict_crop(img, top_k=5))
print("invertida:", classifier.debug_predict_crop(255 - img, top_k=5))