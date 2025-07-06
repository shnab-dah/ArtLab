import matplotlib.pyplot as plt
import cv2
import numpy as np
import os
from tqdm import tqdm
from multiprocessing import Pool, cpu_count

DATA_PATH = 'MSI'
OUTPUT_PATH = 'EXPORT'

def process_folder(folder):
    images = [os.path.join(DATA_PATH, folder, i) for i in os.listdir(os.path.join(DATA_PATH, folder))]
    n_bands = len(images)
    img_shape = cv2.imread(images[0]).shape[:2]
    MB_img = np.zeros((img_shape[0], img_shape[1], n_bands))

    for i in range(n_bands):
        temp_image = cv2.imread(images[i])
        MB_img[:, :, i] = temp_image[:, :, 0]

    MB_matrix = np.zeros((MB_img[:, :, 0].size, n_bands))

    for i in range(n_bands):
        MB_array = MB_img[:, :, i].flatten()
        MB_arrayStd = (MB_array - MB_array.mean()) / MB_array.std()
        MB_matrix[:, i] = MB_arrayStd

    MB_img = 0
    temp_image = 0

    cov = np.cov(MB_matrix.transpose())

    EigVal, EigVec = np.linalg.eig(cov)

    os.makedirs(os.path.join(OUTPUT_PATH, folder), exist_ok=True)
    matrix_output = os.path.join(OUTPUT_PATH, folder, 'matrix.png')
    plt.imshow(cov, cmap='viridis')
    plt.colorbar(label='Covariance')
    plt.title("Covariance Matrix")
    plt.savefig(matrix_output, dpi=300, bbox_inches='tight')
    plt.close()

    filenames_output = os.path.join(OUTPUT_PATH, folder, 'filenames.txt')
    with open(filenames_output, 'w') as f:
        for idx, image in enumerate(images):
            f.write(f"{idx}: {os.path.basename(image)}\n")

    PC = np.matmul(MB_matrix, EigVec)

    PC_2d = np.zeros((img_shape[0], img_shape[1], n_bands))

    for i in range(n_bands):
        PC_2d[:, :, i] = PC[:, i].reshape(-1, img_shape[1])

    PC_2d_Norm = np.zeros((img_shape[0], img_shape[1], n_bands))
    for i in range(n_bands):
        PC_2d_Norm[:, :, i] = cv2.normalize(PC_2d[:, :, i],
                                            np.zeros(img_shape), 0, 255, cv2.NORM_MINMAX)

    pc_output = os.path.join(OUTPUT_PATH, folder, 'PC')
    os.makedirs(pc_output, exist_ok=True)

    for i in range(n_bands):
        plt.imsave(fname=os.path.join(pc_output, f"{i}.png"), arr=PC_2d_Norm[:, :, i], cmap='viridis_r',
                   format='png')
        plt.close()

if __name__ == '__main__':
    DATA_PATH = 'MSI'
    folders = [f for f in os.listdir(DATA_PATH)]

    num_processes = 7 # set how many concurrent can run
    with Pool(num_processes) as pool:
        list(tqdm(pool.imap(process_folder, folders), total=len(folders)))
