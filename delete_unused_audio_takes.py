#!/usr/bin/env python

"""
Deletes unused audio takes from the currently opened project's media pool AND the corresponding files from disk
Example usage: delete_unused_audio_takes.py
"""

import re
import os
import sys

from python_get_resolve import GetResolve

def IsUnusedAudioTake(clip):
  isUnused = int(clip.GetClipProperty("Usage")) == 0
  isAudio = clip.GetClipProperty("Type") == "Audio"
  hasMatchingFilename = re.match("[^_]+_\d{3}_[A-Z0-9]{5}\\.wav", clip.GetClipProperty("File Name"))
  return isAudio and hasMatchingFilename and isUnused  

def DisplayUnusedAudioTakes(folder, displayShift):
    print(displayShift + "- " + folder.GetName())
    found = 0
    
    clips = folder.GetClipList()
    for clip in clips:
        if IsUnusedAudioTake(clip):
          print(displayShift + "  " + clip.GetClipProperty("File Path"))
          found += 1

    displayShift = "  " + displayShift

    folders = folder.GetSubFolderList()
    for folder in folders:
        found += DisplayUnusedAudioTakes(folder, displayShift)
    return found

def DeleteUnusedAudioTakes(mediaPool, folder):
    clips = folder.GetClipList()
    to_delete = list()

    for clip in clips:
        if IsUnusedAudioTake(clip):
          path = clip.GetClipProperty("File Path")
          os.remove(path)
          print('Deleted ' + path)
          to_delete.append(clip)

    if len(to_delete):
      mediaPool.DeleteClips(to_delete)

    folders = folder.GetSubFolderList()
    for folder in folders:
        DeleteUnusedAudioTakes(mediaPool, folder)
    return

# Get currently open project
resolve = GetResolve()

if resolve == None:
  print("Resolve is not running")
  sys.exit(0)

projectManager = resolve.GetProjectManager()
project = projectManager.GetCurrentProject()
mediaPool = project.GetMediaPool()

print("Unused audio takes for project '" + project.GetName() +"':\n")
count = DisplayUnusedAudioTakes(mediaPool.GetRootFolder(), "  ")

if count > 0:
  user_input = input("\nDelete " + str(count) + " items from media pool AND disk? [y/N]")

  if user_input.lower() == 'y' or user_input.lower() == 'yes':
    DeleteUnusedAudioTakes(mediaPool, mediaPool.GetRootFolder())
else:
  print("\nNothing to do.")