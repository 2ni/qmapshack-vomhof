## about
GPX generator with all farms from [vomhof ch](https://vomhof.ch). Can be imported in [qmapshack](https://github.com/Maproom/qmapshack/wiki) so you can plan your routes passing by some farmers.

<img src="qmapshack.png" width="400" />

## how to create vomhof.gpx
Generate a new file or just use the one from the repo.
```
python run.gpx --readcache --writecache
or
python run.gpx --help
```

## import
In qmapshack just call File/Load GIS Data.
Red   = normal farm
Blue  = bio farm
Green = demeter farm

## installation
```
pyenv versions
pyenv virtualenv 3.9.0 vomhof
pyenv local vomhof
pip install -r requirements.txt
