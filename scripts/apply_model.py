"""
Apply trained model

"""
import configparser
import torch
import torch.nn as nn
from torchvision import datasets, transforms
import pandas as pd
import numpy as np
import os

from PIL import Image
import matplotlib.pyplot as plt

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')

def load_data(path):

    im_to_cons = pd.read_csv(path)


    im_to_cons.head()

    # turn the data into a PyTorch Tensor
    data_transforms = {
        'transform': transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
    }
    # print(data_transforms)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu'); device
    # print(device)
    model_ft = torch.load(os.path.join(BASE_PATH, 'trained_model.pt')).to(device)
    # print(model_ft)

    # print(model_ft.classifier)

    # now we "rip" off the final layers so we can extract the 4096-size feature vector
    ripped = model_ft.classifier
    del ripped[6]
    del ripped[5]
    del ripped[4]
    ripped

    unique_ims = im_to_cons.drop_duplicates(subset='images'); unique_ims.shape

    feats = np.zeros((unique_ims.shape[0],4096))

    ims = unique_ims['images'].values

    #return model_ft, device, data_transforms

    def filename_to_im_tensor(file):
        im = plt.imread(file)[:,:,:3]
        im = data_transforms['transform'](im)
        return im[None].to(device)

    #def forward_pass(model_ft, device, data_transforms):

    model_ft.eval() # evaluate mode, no gradient tracking
    i = 0
    batch_size = 4
    # I use the original download directory because it contains unique images
    # each index of feats will correspond to each index of ims
    path = os.path.join(DATA_PROCESSED, 'ims_malawi_2016')
    pre = path + '/{}'

    # iterations = len(ims) - 10000#23385
    # # this approach uses batching and should offer a speed-up over passing one
    # # image at a time by nearly 10x
    # # runtime should be 5-7 minutes vs 45+ for a full forward pass
    # while i + batch_size < iterations:

    #     ims_as_tensors = torch.cat([
    #         filename_to_im_tensor(pre.format(ims[i+j])) for j in range(batch_size)], 0)
    #     feats[i:i+batch_size,:] = model_ft(ims_as_tensors).cpu().detach().numpy()
    #     i += batch_size
    #     if i % 100 == 0:
    #         print(i, end=', ')

    # # does the final batch of remaining images
    # if iterations - i != 0:

    #     rem = iterations - i
    #     ims_as_tensors = torch.cat([filename_to_im_tensor(pre.format(ims[i+j])) for j in range(rem)], 0)
    #     feats[i:i+rem,:] = model_ft(ims_as_tensors).cpu().detach().numpy()
    #     i += rem

    # # save them for safekeeping
    # np.save(os.path.join(DATA_PROCESSED, 'forward_feats_trained_model.npy'), feats)

    feats = np.load(os.path.join(DATA_PROCESSED, 'forward_feats_trained_model.npy'))

    unique_ims = unique_ims[['images']]
    # this will be joined with the main df to show what index you should be looking at in feats
    unique_ims['feat_index'] = np.arange(len(unique_ims))

    im_to_cons = pd.merge(left=im_to_cons, right=unique_ims, on='images')

    group = im_to_cons.groupby(['clust_lat', 'clust_lon'])

    num_clusts = len(group); num_clusts



    ###########Aggregate features
    x = np.zeros((num_clusts, 4096))
    y = []

    # this goes through each cluster group and finds all images that are in the cluster
    # it aggregates the features for those images across the cluster
    for i, g in enumerate(group):
        lat, long = g[0]
        im_sub = im_to_cons[(im_to_cons['clust_lat'] == lat) & (im_to_cons['clust_lon'] == long)].reset_index(drop=True)
        agg_feats = np.zeros((len(im_sub), 4096))
        for j, d in im_sub.iterrows():
            agg_feats[j,:] = feats[d.feat_index]
        agg_feats = agg_feats.mean(axis=0) # averages the features across all images in the cluster

        x[i,:] = agg_feats
        y.append(g[1]['consumption'].values[0])

    y = np.array(y)
    y_log = np.log(y) # try predicting consumption and log consumption

    # ##########Prediction

    # # This is a bunch of code from the Jean et al Github that is modified to work with Python3 and our data


    import random
    from scipy import stats
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import KFold
    import sklearn.linear_model as linear_model
    from matplotlib.collections import EllipseCollection
    import seaborn as sns


    def predict_consumption(
        X, y, k=5, k_inner=5, points=10,
            alpha_low=1, alpha_high=5, margin=0.25):
        """
        Plots predicted consumption.

        """
        y_hat, r2 = run_cv(X, y, k, k_inner, points,
            alpha_low, alpha_high)

        return X, y, y_hat, r2


    def run_cv(X, y, k, k_inner, points, alpha_low,
        alpha_high, randomize=False):
        """
        Runs nested cross-validation to make predictions
        and compute r-squared.

        """
        alphas = np.logspace(alpha_low, alpha_high, points)
        r2s = np.zeros((k,))
        y_hat = np.zeros_like(y)
        kf = KFold(n_splits=k, shuffle=True)
        fold = 0
        for train_idx, test_idx in kf.split(X):
            r2s, y_hat, fold = evaluate_fold(
                X, y, train_idx, test_idx, k_inner, alphas, r2s,
                y_hat, fold, randomize)

        return y_hat, r2s.mean()


    def scale_features(X_train, X_test):
        """
        Scales features using StandardScaler.

        """
        X_scaler = StandardScaler(with_mean=True, with_std=False)
        X_train = X_scaler.fit_transform(X_train)
        X_test = X_scaler.transform(X_test)

        return X_train, X_test


    def train_and_predict_ridge(alpha, X_train, y_train, X_test):
        """
        Trains ridge model and predicts test set.

        """
        ridge = linear_model.Ridge(alpha)
        ridge.fit(X_train, y_train)
        y_hat = ridge.predict(X_test)

        return y_hat


    def predict_inner_test_fold(X, y, y_hat, train_idx,
        test_idx, alpha):
        """
        Predicts inner test fold.

        """
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        X_train, X_test = scale_features(X_train, X_test)
        y_hat[test_idx] = train_and_predict_ridge(
            alpha, X_train, y_train, X_test)

        return y_hat


    def find_best_alpha(X, y, k_inner, alphas):
        """
        Finds the best alpha in an inner CV loop.
        """
        kf = KFold(n_splits=k_inner, shuffle=True)
        best_alpha = 0
        best_r2 = 0
        for idx, alpha in enumerate(alphas):
            y_hat = np.zeros_like(y)
            for train_idx, test_idx in kf.split(X):
                y_hat = predict_inner_test_fold(
                    X, y, y_hat, train_idx, test_idx, alpha)
            r2 = stats.pearsonr(y, y_hat)[0] ** 2
            if r2 > best_r2:
                best_alpha = alpha
                best_r2 = r2
        print('best alpha', best_alpha)

        return best_alpha


    def evaluate_fold(
        X, y, train_idx, test_idx, k_inner, alphas, r2s,
        y_hat, fold,randomize):
        """
        Evaluates one fold of outer CV.
        """
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        if randomize:
            random.shuffle(y_train)

        best_alpha = find_best_alpha(
            X_train, y_train, k_inner, alphas)

        X_train, X_test = scale_features(X_train, X_test)

        y_test_hat = train_and_predict_ridge(
            best_alpha, X_train, y_train, X_test)

        r2 = stats.pearsonr(y_test, y_test_hat)[0] ** 2
        r2s[fold] = r2
        y_hat[test_idx] = y_test_hat

        return r2s, y_hat, fold + 1


    _, _, _, r2 = predict_consumption(x, y_log)
    print('r2: Consumption predicted on x and y_log {}'.format(r2))

    _, _, _, r2 = predict_consumption(x, y)
    print('r2: Consumption predicted on x and y {}'.format(r2))

    # let's use 70% of the data for training
    n_train = int(0.7*(len(x)))
    inds = np.arange(len(x))
    train_ind = np.random.choice(inds, n_train, replace=False)
    valid_ind = np.delete(inds, train_ind)

    train_x = x[train_ind]
    valid_x = x[valid_ind]

    train_y = y_log[train_ind]
    valid_y = y_log[valid_ind]

    ss = StandardScaler() # standardize features
    train_x = ss.fit_transform(train_x)
    valid_x = ss.transform(valid_x)

    # let's make sure we don't have vastly different distributions
    # of train/test
    train_y.mean(), valid_y.mean()

    ridge = linear_model.Ridge()
    ridge.fit(train_x, train_y)
    ridge.score(train_x, train_y)

    # ??? what happened ???
    # well, ridge regression is heavily affected by alpha
    # (regularization) value Jean et. al. code finds a good alpha,
    # which we do not do here if we use theirs, our ridge score will go up
    ridge.score(valid_x, valid_y)

    ridge2 = linear_model.Ridge(alpha=70) # the best alphas printed
    #suggest using a high alphas
    ridge2.fit(train_x, train_y)
    ridge2.score(train_x, train_y)

    # this is closer to the r^2 using the paper's functions, as seen above
    # they did other things like CV and identifying best alphas
    # this was just meant to show a quick and dirty way of testing
    ridge2.score(valid_x, valid_y)

    ########Plots
    preds = ridge2.predict(valid_x)
    print(preds)
    plt.figure(figsize=(8,5))
    plt.scatter(valid_y, preds, alpha=0.6)
    plt.plot(np.unique(valid_y), np.poly1d(np.polyfit(valid_y, preds, 1))(np.unique(valid_y)), color='g')
    plt.text(2.4, 1.5, 'r^2=0.43', size=12)
    plt.xlabel('Actual Log Consumption($/day)')
    plt.ylabel('Predicted Log Consumption($/day)')
    plt.title('Malawi Results')
    plt.savefig(os.path.join(DATA_PROCESSED, 'prediction_plot.png'))

    return print('Completed')

if __name__ == '__main__':

    country = 'MWI'
    path = os.path.join(DATA_INTERMEDIATE, country, 'mw_full_guide.csv')

    load_data(path)

    # forward_pass(model_ft, device, data_transforms)
