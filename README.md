# syncprojects-web
[![Build Status](https://ci.keane.space/api/badges/keaneokelley/syncprojects-web/status.svg)](https://ci.keane.space/keaneokelley/syncprojects-web)
`syncprojects-web` is the web interface for Syncprojects. It serves an API for consumption by [syncprojects-client](https://github.com/k3an3/syncprojects-client) and facilitates control over sync features, though it is envisoned to do a lot more. `syncprojects-web` could be the hub of a music production project, as well as a place to augment the songwriting process with various tools (much of which hasn't been developed yet...).

The application is built with Django, and also uses the Django REST Framework and Django Channels. Bootstrap 5 was used to build the UI, though UI is not my strong suit.

Note that due to some licensing restrictions of 3rd party code, one of the audio player components has been forcefully stripped out of this version.

![Syncprojects Web](https://github.com/k3an3/syncprojects-web/static/img/readme1.png)

## Features
* Control the `syncprojects-client` application; trigger the client to sync or open the DAW/project. Changelog for DAW project changes.
* Acts as central database for sync, audio upload history
* Allows users to comment on songs and projects, and mark comments as resolved/unresolved. Comments can be tied to a specific moment in the song, a la the Soundcloud player.
* Basic project todo lists
* Customized audio player (pictured above) allows creation of custom regions that can be labelled and looped. Useful for practicing/analyzing a part of a song, or conveying structure during songwriting.
* Basic notifications

### Possible Future Features
* A lyric editor. Collaborative like Google Drive, but maybe have a way to bind phrases to parts of the song?
* Allow multiple users to have a shared audio player session
* Management of band/project members, followers, etc.
* Tracking of band/project expenses/income
* Social features
* S3/cloud auth actually secure
