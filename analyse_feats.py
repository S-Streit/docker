import pandas as pd
from sklearn.cluster import KMeans
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image
import os


class FeatureAnalysis():

    def __init__(self, path, server=True):

        self.parent_path = path
        self.feat_frame_paths = self.get_paths()



    def get_paths(self):

        frame_list = []
        for folder in os.listdir(parent_path):

            feat_frame = os.path.join(folder, "features_frame.csv")
            if os.path.isfile(feat_frame):
                frame_list.append(feat_frame)

        print(frame_list)

        return frame_list

    def check_kmeans(self, data, paths):

        res = list()
        n_cluster = range(20,500,20)

        for n in n_cluster:
            print("Checking for {0} Clusters...".format(n))
            kmeans = KMeans(n_clusters=n)
            kmeans.fit(data)
            res.append(kmeans.inertia_)

        plt.plot(n_cluster, res)
        plt.title('elbow curve')
        plt.savefig("elbow_curve.png")
        # plt.show()

        return 2

    def kmeans_plot(self, data, paths, k=20):
        kmeans = KMeans(n_clusters=k, random_state=0).fit(data)
        centroids = kmeans.cluster_centers_

        # print(centroids)
        dirname = "{0}_clusters".format(k)

        if not os.path.isdir(dirname):
            os.makedirs(dirname)

        for n, center in enumerate(centroids):
            fig, ax = plt.subplots(3,3)
            fig.suptitle("Center: {0} | Patch: {1}".format(n, paths[n]))
            
            distances = np.argsort(np.linalg.norm(data - center, axis=1))
            cen = distances[0]


            for ind, a in enumerate(ax.flatten()):
                dist = distances[ind]
                # print(paths[dist])
                with Image.open(paths[dist]) as im:
                    patch_img = im.copy()


                a.imshow(patch_img)
                a.axis("off")
            # ax[int(n%3), n].imshow(patch_img)

            plt.savefig(os.path.join(dirname, "cluster_{0}.png".format(n)))

        # plt.show()


    def check_on_server(self):

        csv_path = "/home/simon/philipp/docker/features_frame.csv"
        data_ = pd.read_csv(csv_path)
        data = data_.iloc[:, 1:].values
        paths = [d[0] for d in data_.iloc[:, :1].values]
        # print(paths)
        # print(data)
        # k = check_kmeans(data, paths)

        kmeans_plot(data, paths)

if __name__ == "__main__":

    path = "/home/simon/philipp/patches"
    fa = FeatureAnalysis(path)
    # check_on_server()

    # patch_path = "/media/user/easystore/patches/"
    # patch_path_ = "/media/user/easystore/DigitalSlide_A1M_9S_1_20190127165819218/"
    # csv_path = "/home/user/Documents/Master/docker/features_frame.csv"
    # csv_path_low = "/home/user/Documents/Master/docker/features_frame_low_att.csv"


    # num_patches = -1

    # data_ = pd.read_csv(csv_path)
    # data = data_.iloc[:, 1:].values[:num_patches]

    # data_low_ = pd.read_csv(csv_path_low)
    # data_low = data_low_.iloc[:, 1:].values[:num_patches]

    # paths = [p[0].replace("/home/simon/philipp/", patch_path) for p in data_.iloc[:, :1].values]
    # paths_low = [p[0].replace("/home/simon/philipp/patches/", patch_path) for p in data_low_.iloc[:, :1].values]


    # all_data = np.concatenate((data[:num_patches], data_low[:num_patches]))
    # all_paths = np.concatenate((paths[:num_patches], paths_low[:num_patches]))


    # # k = check_kmeans(all_data, all_paths)
    # kmeans_plot(all_data, all_paths)
    