import h5py
import cPickle as pickle
from dset_paths import BROWN_CORPUS_DATA_FILE, BROWN_CORPUS_VOCAB_FILE

# TODO Set up so only loads parts of dataset (a few files)
# at a time for large datasets

class Dataset(object):

    def __init__(self, feat_dim, batch_size):
        self.ind = 0
        self.feat_dim = feat_dim
        self.batch_size = batch_size
        self.data = None
        self.data_ind = 0

    def data_left(self):
        return self.data_ind < self.data.shape[1]

    def get_batch(self):
        raise NotImplementedError()

    def restart(self):
        ''' For starting a new epoch '''
        self.data_ind = 0


class BrownCorpus(Dataset):

    # TODO Labels are last rows of the data matrix

    def __init__(self, feat_dim, batch_size, subset='train'):
        super(BrownCorpus, self).__init__(feat_dim, batch_size)
        # Load vocab
        with open(BROWN_CORPUS_VOCAB_FILE, 'rb') as fin:
            self.word_inds = pickle.load(fin)
        self.words = dict((v, k) for k, v in self.word_inds.iteritems())
        # Load data matrices
        h5f = h5py.File(BROWN_CORPUS_DATA_FILE, 'r')
        self.subset = subset

        # NOTE These are all just word indices, no point
        # in putting them on the GPU
        if subset == 'train':
            self.data = h5f['train'][...]
        elif subset == 'dev':
            self.data = h5f['dev'][...]
        elif subset == 'test':
            self.data = h5f['test'][...]

        self.labels = self.data[-1, :]

    def get_batch(self):
        self.batch = self.data[:-1, self.data_ind:self.data_ind+self.batch_size]
        self.batch_labels = self.labels[self.data_ind:self.data_ind+self.batch_size]
        self.data_ind += self.batch.shape[1]
        return self.batch, self.batch_labels
