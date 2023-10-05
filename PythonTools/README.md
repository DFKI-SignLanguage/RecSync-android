# RecSync PostProcessing

This utility "repairs" the videos generated by the RecSyncNG app:
* Videos are unpacked
* Missing frames are injected as black frames
* Frame sequences are "synchronized" to have the same number of frames and the same start time (with tolerance) 
* Videos are re-packed, and they will all have the same starting frame and the same number of frames
  * A frame counter is added

## Installing

Create an environment and install the packages listed in the `requirements.txt`

## Usage

python PostProcessVideos -i <indir> -o <outdir>

Where the <indir> contains a record session downloaded from the RemoteController. E.g.:

```
<indir>>/
  6f7532c944f79e3a
  66b1966da6295638
  93d5ee73b24785b2
  9426ca37884d5237
  a7ca3cbd2ffb0d76
  b754970550f1257f
  cb5ca011d1918b50
  e1791b49dcdc60dd
```

The output dir will be filled with the post-processed videos, plus a `_done` file tagging that all the client videos where correctly post-processed. E.g.:

```
<outdir>/
  _done
  6f7532c944f79e3a.csv
  6f7532c944f79e3a.mp4
  66b1966da6295638.csv
  66b1966da6295638.mp4
  ...
```

## Batch parallel processing

There is a Makefile helping in the processing of several directories, to post-process a whole set of sessions in a single shot.

```
cd PostProcessing
export RECSYNC_DOWNLOAD_DIR=path/to/downloaded/sessions
make -j 8
```


## Testing

Export an environment variable with the root of your test material and run the `pytest` command.
It is the directory containing the clients subdirs.

```bash
export RECSYNCH_SESSION_DIR=path/to/my/stuff
pytest
```