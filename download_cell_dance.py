from allensdk.core.cell_types_cache import CellTypesCache
import pandas as pd
from sklearn import manifold
import scipy.signal

def get_rheobase_response(ctc, cell_id):
    cells = ctc.get_cells()
    ef = pd.DataFrame.from_records(ctc.get_ephys_features())
    thumb_sweep_id = ef[ef.specimen_id == cell_id].thumbnail_sweep_id.values[0]
    
    sweeps = ctc.get_ephys_sweeps(cell_id)
    thumb_sweep = next(s for s in sweeps if s['id'] == thumb_sweep_id)

    thumb_sweep_num = thumb_sweep['sweep_number']
                                   
    ds = ctc.get_ephys_data(specimen_id=cell_id)
    swp = ds.get_sweep(thumb_sweep_num)
        
    idxs = np.argwhere(np.diff(swp['stimulus']))
    start = idxs[-2][0]
    end = idxs[-1][0]
    
    resample_factor = int(swp['sampling_rate'] / 50000.0)

    resp = swp['response'][start:end]
    if resample_factor > 1.0:
        resp = scipy.signal.decimate(resp, resample_factor)
    return resp

ctc = CellTypesCache(manifest_file="/data/dynamic-brain-workshop/cell_types_cache/cell_types_manifest.json")
ef = ctc.get_ephys_features()
cells = ctc.get_cells()

efdf = pd.DataFrame.from_records(ef)
efdf_nonan = efdf.dropna()

xfm = manifold.TSNE(n_components=2)
pos = xfm.fit_transform(efdf_nonan.drop(['rheobase_sweep_id', 'id', 'thumbnail_sweep_id', 'specimen_id'], axis=1).values)

cres = []
cre_ids = {}
for cid in efdf_nonan.specimen_id:
    cre = next(c['transgenic_line'] for c in cells if c['id'] == cid)
    if cre not in cre_ids:
        cre_ids[cre] = len(cre_ids)
    
    cres.append(cre_ids[cre])

resps = []
for i, cell_id in enumerate(efdf_nonan.specimen_id):
    print("extracted %d/%d" % (i+1, len(efdf_nonan)))
    resp = get_rheobase_response(ctc, cell_id)
    resps.append(resp)

arr = np.array(resps)
np.savez_compressed('cell_dance.npz', pos=pos, arr=arr, cres=np.array(cres))