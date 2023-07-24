# wrap-your-spotify-v2
analyze your spotify data, updated version of [this project](https://github.com/mayonnaisical/wrap-your-spotify). The old one has a few more features around sorting by artist and stuff but the code in v2 is much simpler, i have no idea how any of v1 works anymore lol

## how to use
download your _extended_ spotify data from [here](https://www.spotify.com/ca-en/account/privacy/) and place the `MyData` you get from it in the same directory as the python script.

i have it set up to print a handful of things i found interesting for myself, i don't think it's too terribly hard to modify it to print out different things

## depedancies and stuff
it uses `match` so not compatible with versions of Python before that was added, but should be fairly simple to modify to get it working on versions before that
it also uses colorama 0.4.6 and tqdm 4.61.1 which i know i had to install, also uses glob but idk if that comes with python. also datetime and dateutil but i'm pretty sure those are
