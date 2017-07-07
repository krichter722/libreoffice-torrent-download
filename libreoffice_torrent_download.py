#!/usr/bin/python

import plac
import urllib
import re
import tempfile
import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger_stdout_handler = logging.StreamHandler()
logger_stdout_handler.setLevel(logging.DEBUG)
logger_formatter = logging.Formatter('%(asctime)s:%(message)s')
logger_stdout_handler.setFormatter(logger_formatter)
logger.addHandler(logger_stdout_handler)

base_url_default = "http://download.documentfoundation.org/libreoffice/"

@plac.annotations(output_dir=("a directory where to put the downloaded torrents into (the script will generate and use a temporary directory if no value is specified)", "option"),
    skip_existing=("skip downloading if the resulting torrent filename is already present in the output directory", "flag"),
)
def libreoffice_torrent_download(base_url=base_url_default, output_dir=None, skip_existing=False, extensions=[".tar.gz", ".tar.xz", ".tar.bz2", ".msi", ".dmg", ".paf.exe", ".flatpak", ".iso"], architectures=["x86", "x86_64"], platforms=["deb", "mac", "rpm", "win"], binary_branches=["stable", "testing"], portable_branches=["src", "portable", "flatpack", "box"]):
    if output_dir is None:
        output_dir = tempfile.mkdtemp(suffix="libreoffice-torrent-download")
        logger.info("using temporary directory '%s' for output of downloaded torrents" % (output_dir,))
    elif not os.path.exists(output_dir):
        logger.info("creating inexisting output directory '%s'" % (output_dir,))
        os.makedirs(output_dir)
    for binary_branch in binary_branches:
        url_retrieve_result = urllib.urlretrieve(os.path.join(base_url, binary_branch))
        url_data = open(url_retrieve_result[0]).read()
        versions = re.findall("[0-9]\\.[0-9]\\.[0-9]", url_data)
        versions = set(versions)
            # set necessary to remove duplicates
        logger.debug("found versions '%s' for binary branch '%s'" % (versions, binary_branch))
        for version in versions:
            for platform in platforms:
                for architecture in architectures:
                    __download_torrent__(url=os.path.join(base_url, binary_branch, version, platform, architecture), output_dir=output_dir, extensions=extensions, skip_existing=skip_existing)
    for portable_branch in portable_branches:
        url_retrieve_result = urllib.urlretrieve(os.path.join(base_url, portable_branch))
        url_data = open(url_retrieve_result[0]).read()
        versions = re.findall("[0-9]\\.[0-9]\\.[0-9]", url_data)
        versions = set(versions)
            # set necessary to remove duplicates
        logger.debug("found versions '%s' for portable branch '%s'" % (versions, portable_branch))
        for version in versions:
            __download_torrent__(url=os.path.join(base_url, portable_branch, version), output_dir=output_dir, extensions=extensions, skip_existing=skip_existing)


def __download_torrent__(url, output_dir, extensions, skip_existing):
    url_retrieve_result = urllib.urlretrieve(url)
    tmp_file_path = url_retrieve_result[0]
    url_data = open(tmp_file_path).read()
    matches = re.findall(r'href=[\'"]?([^\'" >]+)', url_data)
        # errornous syntax highlighting in gedit 3.22.0 reported at https://bugzilla.gnome.org/show_bug.cgi?id=784673
    logger.debug("found matches '%s' for url '%s'" % (matches, url,))
    for match in matches:
        extension_match = False
        for extension in extensions:
            if match.endswith(extension):
                extension_match = True
                break
        if extension_match:
            logger.debug("found matching download '%s'" % (match,))
            torrent_url = os.path.join(url, match)+".torrent"
            torrent_filename = os.path.join(output_dir, match)+".torrent"
            if skip_existing and os.path.exists(torrent_filename):
                logger.info("skipping existing torrent file '%s'" % (torrent_filename,))
                continue
            try:
                logger.debug("trying to download torrent '%s' to file '%s'" % (torrent_url, torrent_filename))
                torrent_retrieve_result = urllib.urlretrieve(torrent_url, filename=torrent_filename)
            except Exception as ex:
                logger.debug("download of torrent '%s' failed (might not exist) (exception was '%s')" % (torrent_url, str(ex)))
            

if __name__ == "__main__":
    plac.call(libreoffice_torrent_download)
