import os







if __name__ == "__main__":
    folder_path = "/home/user/Documents/Master/data"

    for subfolder in os.listdir(folder_path):
        print(subfolder)