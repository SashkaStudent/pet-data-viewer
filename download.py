#!/usr/bin/env python3
# download.py: Download geomagnetic data from Edinburgh GIN
#
# This script is designed to download geomagnetic data
# from the Edinburgh INTERMAGNET Geomagnetic Information Node.
# To use the script, follow these steps:
#
# 1.) Create a new directory.
# 2.) Move to the new directory and copy the script there.
# 3.) Execute the script by typing 'python3 download.py'.
#
# The script keeps track of its progress through the list of files
# to download. If it fails at any time, you can restart it and it will
# resume at the point where it failed.
#
#
import os
import sys
import shutil
import re
from urllib import request
from urllib.error import URLError
from contextlib import ExitStack


# Configurable parameters - these variables control use of proxy
# servers at the users site - there's also an option to use
# authentication - change them as required (though the
# defaults should work OK)
gin_username = ''
gin_password = ''
proxy_address = ''
n_retries = 4
#
#
#----------------------------------------------------------------------
# upd_op_co:         Increment and serialize the operation count
# Input parameters:  op_count the current operation number
# Returns:           op_count is incremented and returned (and written to disk)
def upd_op_co(op_count):
  op_count = op_count + 1
  with open('counter.dat', 'w') as f:
    f.write('%d' % op_count)
  return op_count

#----------------------------------------------------------------------
# safemd:            Safely create a folder (no error if it already exists)
# Input parameters:  folder the directory to create
#                    op_number the operation number for this call
#                    op_count the current operation number
# Returns:           op_count is incremented and returned (and written to disk)
def safemd (folder, op_number, op_count):
  if op_number >= op_count:
    if op_number == 0:
      print ('Creating directories...')
    try:
      os.makedirs (folder, exist_ok=True)
    except OSError:
      print ('Error: unable to create directory: ' + str(folder))
      sys.exit (1)
    op_count = upd_op_co (op_count)
  return op_count

#----------------------------------------------------------------------
# getfile:           Download a file from a web server
# Input parameters:  url URL to download from
#                    local_file local file to download to
#                    n_retries number of retries to do
#                    op_number the operation number for this call
#                    gin_username the username of the GIN (or empty string)
#                    gin_password the username of the GIN (or empty string)
#                    proxy_address address of proxy server (or empty string)
#                    n_folders the number of folders to create
#                    n_downloads the number of files to download
#                    op_count the current operation number
# Returns:           op_count is incremented and returned (and written to disk)
def getfile (url, local_file, n_retries, op_number, gin_username,
             gin_password, proxy_address, n_folders,
             n_downloads, op_count):
  if op_number >= op_count:
    # tell the user what's going on
    percent = ((op_number - n_folders) * 100) / n_downloads
    print ('%d%% - downloading file: %s' % (percent, local_file))
    
    # remove any existing file
    try:
      os.remove (local_file)
    except FileNotFoundError:
      pass
    except OSError:
      print ('Error: unable to remove file: ' + str(local_file))
      sys.exit (1)
    
    # handle authentication and proxy server
    proxy = auth = None
    if len (proxy_address) > 0:
      proxy = req.ProxyHandler({'http': proxy_address, 'https': proxy_address})
    if len (gin_username) > 0:
      auth = req.HTTPBasicAuthHandler()
      auth.add_password (realm=None,
                         uri='https://imag-data.bgs.ac.uk/GIN_V1',
                         user=gin_username,
                         passwd=gin_password)
    if url.startswith ('https'):
      default_handler = request.HTTPSHandler
    else:
      default_handler = request.HTTPHandler
    if auth and proxy:
      opener = request.build_opener(proxy, auth, default_handler)
    elif auth:
      opener = request.build_opener(auth, default_handler)
    elif auth:
      opener = request.build_opener(proxy, default_handler)
    else:
      opener = request.build_opener(default_handler)
    
    # download the file
    success = False
    while (not success) and (n_retries > 0):
      try:
        with opener.open (url) as f_in:
          with open (local_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out, 4096)
        success = True
      except (URLError, IOError, OSError):
        n_retries -= 1
    if not success:
      print ('Error: cannot download ' + local_file)
      sys.exit (1)
    
    # rename IAGA-2002 files
    dt = None
    try:
      with open(local_file, 'r') as f:
        for line in f.readlines():
          if re.search ('^ Data Type', line):
            dt = line[24:25].lower()
    except (IOError, OSError):
      pass
    if dt:
      if not dt.isalpha():
        dt = None
    if dt:
      new_local_file = local_file[:len(local_file) - 7] + dt + local_file[len(local_file) - 7:]
      try:
        os.remove (new_local_file)
      except (FileNotFoundError, OSError):
        pass
      try:
        os.rename (local_file, new_local_file)
      except (IOError, OSError):
        print ('Warning: unable to rename ' + local_file + ' to ' + new_local_file)
    else:
      print ('Warning: unable to determine data type for renaming of ' + local_file)
    
    op_count = upd_op_co (op_count)
  return op_count

if __name__ == '__main__':
  # are we restarting a failed operation or starting from new
  try:
    with open ('counter.dat') as f:
      op_count = int(f.read())
      print ('Information: resuming download after previous failure')
  except (IOError, ValueError, OSError):
    op_count = 0
  n_folders = 1
  n_downloads = 90

  folder = os.path.join('2017', 'PET')
  op_count = safemd (folder, 0, op_count)
  
  local_file = os.path.join('2017', 'PET', 'pet2017min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2017-01-01&dataDuration=365', local_file, n_retries, 1, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  #local_file = os.path.join('2017', 'PET', 'pet20170908min.min')
  #op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2017-09-08&dataDuration=1', local_file, n_retries, 1, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  
  
  """
  local_file = os.path.join('2022', 'PET', 'pet20220102min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-01-02&dataDuration=1', local_file, n_retries, 2, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220103min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-01-03&dataDuration=1', local_file, n_retries, 3, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220104min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-01-04&dataDuration=1', local_file, n_retries, 4, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220105min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-01-05&dataDuration=1', local_file, n_retries, 5, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220106min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-01-06&dataDuration=1', local_file, n_retries, 6, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220107min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-01-07&dataDuration=1', local_file, n_retries, 7, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220108min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-01-08&dataDuration=1', local_file, n_retries, 8, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220109min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-01-09&dataDuration=1', local_file, n_retries, 9, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220110min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-01-10&dataDuration=1', local_file, n_retries, 10, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220111min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-01-11&dataDuration=1', local_file, n_retries, 11, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220112min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-01-12&dataDuration=1', local_file, n_retries, 12, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220113min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-01-13&dataDuration=1', local_file, n_retries, 13, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220114min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-01-14&dataDuration=1', local_file, n_retries, 14, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220115min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-01-15&dataDuration=1', local_file, n_retries, 15, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220116min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-01-16&dataDuration=1', local_file, n_retries, 16, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220117min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-01-17&dataDuration=1', local_file, n_retries, 17, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220118min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-01-18&dataDuration=1', local_file, n_retries, 18, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220119min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-01-19&dataDuration=1', local_file, n_retries, 19, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220120min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-01-20&dataDuration=1', local_file, n_retries, 20, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220121min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-01-21&dataDuration=1', local_file, n_retries, 21, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220122min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-01-22&dataDuration=1', local_file, n_retries, 22, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220123min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-01-23&dataDuration=1', local_file, n_retries, 23, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220124min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-01-24&dataDuration=1', local_file, n_retries, 24, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220125min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-01-25&dataDuration=1', local_file, n_retries, 25, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220126min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-01-26&dataDuration=1', local_file, n_retries, 26, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220127min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-01-27&dataDuration=1', local_file, n_retries, 27, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220128min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-01-28&dataDuration=1', local_file, n_retries, 28, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220129min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-01-29&dataDuration=1', local_file, n_retries, 29, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220130min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-01-30&dataDuration=1', local_file, n_retries, 30, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220131min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-01-31&dataDuration=1', local_file, n_retries, 31, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220201min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-02-01&dataDuration=1', local_file, n_retries, 32, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220202min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-02-02&dataDuration=1', local_file, n_retries, 33, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220203min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-02-03&dataDuration=1', local_file, n_retries, 34, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220204min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-02-04&dataDuration=1', local_file, n_retries, 35, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220205min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-02-05&dataDuration=1', local_file, n_retries, 36, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220206min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-02-06&dataDuration=1', local_file, n_retries, 37, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220207min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-02-07&dataDuration=1', local_file, n_retries, 38, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220208min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-02-08&dataDuration=1', local_file, n_retries, 39, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220209min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-02-09&dataDuration=1', local_file, n_retries, 40, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220210min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-02-10&dataDuration=1', local_file, n_retries, 41, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220211min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-02-11&dataDuration=1', local_file, n_retries, 42, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220212min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-02-12&dataDuration=1', local_file, n_retries, 43, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220213min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-02-13&dataDuration=1', local_file, n_retries, 44, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220214min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-02-14&dataDuration=1', local_file, n_retries, 45, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220215min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-02-15&dataDuration=1', local_file, n_retries, 46, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220216min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-02-16&dataDuration=1', local_file, n_retries, 47, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220217min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-02-17&dataDuration=1', local_file, n_retries, 48, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220218min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-02-18&dataDuration=1', local_file, n_retries, 49, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220219min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-02-19&dataDuration=1', local_file, n_retries, 50, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220220min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-02-20&dataDuration=1', local_file, n_retries, 51, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220221min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-02-21&dataDuration=1', local_file, n_retries, 52, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220222min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-02-22&dataDuration=1', local_file, n_retries, 53, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220223min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-02-23&dataDuration=1', local_file, n_retries, 54, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220224min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-02-24&dataDuration=1', local_file, n_retries, 55, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220225min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-02-25&dataDuration=1', local_file, n_retries, 56, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220226min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-02-26&dataDuration=1', local_file, n_retries, 57, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220227min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-02-27&dataDuration=1', local_file, n_retries, 58, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220228min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-02-28&dataDuration=1', local_file, n_retries, 59, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220301min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-03-01&dataDuration=1', local_file, n_retries, 60, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220302min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-03-02&dataDuration=1', local_file, n_retries, 61, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220303min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-03-03&dataDuration=1', local_file, n_retries, 62, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220304min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-03-04&dataDuration=1', local_file, n_retries, 63, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220305min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-03-05&dataDuration=1', local_file, n_retries, 64, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220306min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-03-06&dataDuration=1', local_file, n_retries, 65, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220307min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-03-07&dataDuration=1', local_file, n_retries, 66, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220308min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-03-08&dataDuration=1', local_file, n_retries, 67, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220309min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-03-09&dataDuration=1', local_file, n_retries, 68, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220310min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-03-10&dataDuration=1', local_file, n_retries, 69, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220311min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-03-11&dataDuration=1', local_file, n_retries, 70, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220312min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-03-12&dataDuration=1', local_file, n_retries, 71, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220313min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-03-13&dataDuration=1', local_file, n_retries, 72, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220314min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-03-14&dataDuration=1', local_file, n_retries, 73, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220315min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-03-15&dataDuration=1', local_file, n_retries, 74, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220316min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-03-16&dataDuration=1', local_file, n_retries, 75, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220317min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-03-17&dataDuration=1', local_file, n_retries, 76, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220318min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-03-18&dataDuration=1', local_file, n_retries, 77, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220319min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-03-19&dataDuration=1', local_file, n_retries, 78, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220320min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-03-20&dataDuration=1', local_file, n_retries, 79, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220321min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-03-21&dataDuration=1', local_file, n_retries, 80, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220322min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-03-22&dataDuration=1', local_file, n_retries, 81, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220323min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-03-23&dataDuration=1', local_file, n_retries, 82, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220324min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-03-24&dataDuration=1', local_file, n_retries, 83, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220325min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-03-25&dataDuration=1', local_file, n_retries, 84, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220326min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-03-26&dataDuration=1', local_file, n_retries, 85, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220327min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-03-27&dataDuration=1', local_file, n_retries, 86, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220328min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-03-28&dataDuration=1', local_file, n_retries, 87, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220329min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-03-29&dataDuration=1', local_file, n_retries, 88, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220330min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-03-30&dataDuration=1', local_file, n_retries, 89, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  local_file = os.path.join('2022', 'PET', 'pet20220331min.min')
  op_count = getfile ('https://imag-data.bgs.ac.uk/GIN_V1/GINServices?Request=GetData&format=IAGA2002&testObsys=0&observatoryIagaCode=PET&samplesPerDay=1440&orientation=HDZF&publicationState=adj-or-rep&recordTermination=UNIX&dataStartDate=2022-03-31&dataDuration=1', local_file, n_retries, 90, gin_username, gin_password, proxy_address, n_folders, n_downloads, op_count)
  """
  # tidy up
  print ('100% - data download complete')
  os.remove ('counter.dat')

