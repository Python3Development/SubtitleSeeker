# SubtitleSeeker
Python 3 GUI script that automatically (or manually) downloads subtitles (.srt files) for media files based on the filename. 
It's multithreaded<sup>[1](#fn1)</sup> so it can run multiple tasks at once. 

### Deprecated

*Code remains here for referential purposes*

This project was discontinued because a better and more accurate alternative was found in Kodi. 

#### Procedure
1. Search ~~Google~~ BING/Yahoo with _filename_.ext
2. Browse the first **OpenSubtitles** url
3. Scrape the OpenSubtitles html page
4. Extract the download link
5. Perform a download and write to file _filename_.srt

___

<sub>
<a name="fn1"/>[1] This was originally developed as a single thread/single files script to be used 
as a Windows Context Menu item. It was then updated with a GUI to provide more granular control over the different steps in the downloading
process.
</sub>