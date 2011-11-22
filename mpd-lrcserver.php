<?php
### MPD Subtitles LRC Server ###
# Version 0.3 by Scott Garrett #
# Wintervenom [(at)] gmail.com #
################################
# Changelog:
#
# 0.1
#   Initial version.
#
# 0.2
#   Allow size limits.
#   Allow overwrite control.
#   Use lowercase names to prevent duplicates.
#
# 0.3
#   GET command to list database.
#   GET command to display a particular LRC.
#

$path = 'lrc';
$version = 'mpd-lrcserver-0.3';
$maxsize = 100000; # bytes
$minlines = 3;
$allowoverwrite = True;



function sanitize($string) {
    # Replace non-filename-friendly characters.
    return preg_replace('/[^\w\-\. ]/', '_', strtolower(trim(urldecode($string))));
}



function fuzzypath($path, $destination, $accuracy=3) {
    # Find the closest-matching $destination in $path.
    if ($handle = opendir($path)) {
        while (false !== ($file = readdir($handle))) {
            if (substr($file, 0, 1) !== '.') {
                $score = levenshtein($destination, strtolower($file));
                if ($score < $accuracy) {
                    $match = $file;
                    $accuracy = $score;
                }
            }
        }
        closedir($handle);
        if (empty($match)) return false;
        return "$path/$match";
    } else die('ReadError');
}

function lrclist($path, $level=0) {
    if ($handle = opendir($path)) {
        while (false !== ($file = readdir($handle))) {
            if (substr($file, 0, 1) !== '.') {
                if (is_dir("$path/$file")) {
                    lrclist("$path/$file", $level+1);
                } elseif (substr($file, -4) === '.lrc') {
                    print(basename($path).'/'.substr($file, 0, -4)."\n");
                }
            }
        }
        closedir($handle);
        if (empty($match)) return false;
        return "$path/$match";
    } else die('ReadError');
}


header('Content-type: text/plain; charset=utf-8');
header('Cache-Control: no-store, no-cache, must-revalidate, post-check=0,'
    . 'pre-check=0');

# Need at least artist or title field to do anything.
if (isset($_POST['a']) || isset($_POST['t'])) {
    empty($_POST['a']) and $artist = '_none_'
        or $artist = sanitize($_POST['a']);
    empty($_POST['t']) and $title = '_none_'
        or $title = sanitize($_POST['t']);
    empty($_POST['d']) and $duration = '0'
        or $duration = $_POST['d'];
    # Strip out non-digits from duration value.
    $duration = preg_replace('/[^\d]/', '', $duration);
    # Complain if the duration value isn't usable.
    if (empty($duration)) die('InvalidDuration');
    # Create LRC database path if it doesn't exist.
    if (!file_exists($path)) mkdir($path);
    # If no [l]yric field, assume the database is being queried.
    if (empty($_POST['l'])) {
        # Can we find the $artist?
        $path = fuzzypath($path, $artist) or die('NoMatch');
        # Can we find the song $title with the $duration?
        #   If not, can we find it without?
        $lrc = fuzzypath($path, "$title-$duration.lrc") or
            $lrc = fuzzypath($path, "$title.lrc") or die('NoMatch');
        # Is the result we found an LRC subtitle?
        if (substr($lrc, -4) === '.lrc') {
            # Send it if so.
            header('Content-Description: File Transfer');
            header('Content-Transfer-Encoding: binary');
            header('Content-Disposition: attachment; filename="'.basename($lrc).'"');
            header('Expires: 0');
            readfile($lrc) or die('ReadError');
        } else die('NoMatch');
    } else {
        # Client wants to submit lyrics to the database.
        $lyrics = trim(urldecode($_POST['l']));
        # Complain if client tries to upload something too big.
        if (strlen($lyrics) > $maxsize) die('TooBig');
        # Split and filter out invalid lines from the uploaded lyrics.
        foreach (explode("\n", $lyrics) as $line) {
            $line = trim($line);
            if (preg_match('/^\[(?:\d+:)?(?:\d+:)?\d+(?:\.\d+)?\]|^\[\w{2}:.*\]/', $line))
                $filtered[] = $line;
        }
        # Complain if there aren't enough valid lines in the uploaded lyrics.
        if (count($filtered) < $minlines) die('Invalid');
        # Create artist path if it doesn't exist.
        if (!file_exists("$path/$artist")) mkdir("$path/$artist");
        # If the file already exists, make sure we're allowed to overwrite.
        if (file_exists("$path/$artist/$title-$duration.lrc") &&
            !$allowoverwrite) die('FileExists');
        # Write the LRC file.
        if ($handle = fopen("$path/$artist/$title-$duration.lrc", 'w')) {
            foreach ($filtered as $line)
                fwrite($handle, $line . "\n");
            fclose($handle);
            die('Success');
        } else die('WriteError');
    }
} elseif (isset($_GET['c'])) {
    # Handle GET commands.
    $command = explode(':', trim(urldecode($_GET['c'])), 2);
    empty($command[0]) and die('NoInput');
    switch (strtolower($command[0])) {
    # List all LRCs in the database.
    case 'list':
        lrclist($path);
        break;
    # Display a particular song.
    case 'show':
        empty($command[1]) and die('MissingArgs');
        $params = explode('/', $command[1]);
        empty($params[0]) and $artist = '_none_'
            or $artist = sanitize($params[0]);
        empty($params[1]) and $title = '_none_'
            or $title = sanitize($params[1]);
        if (!file_exists("$path/$artist/$title.lrc")) die('NoMatch');
        readfile("$path/$artist/$title.lrc") or die('ReadError');
        break;
    default:
        die('UnknownCommand');
    }
# Print version if no query.
} else die($version);
?>
