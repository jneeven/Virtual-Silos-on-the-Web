var Pool = require('phantomjs-pool').Pool;
const fs = require('fs');
const exec = require('child_process').exec;
const robots = require('robots');
const parser = new robots.RobotsParser();
const parseDomain = require('parse-domain');

const videoFormats = ['.mkv', '.flv', '.flv', '.vob', '.ogv', '.ogg', '.drc', '.gif', '.gifv', '.mng', '.avi', '.mov', '.qt', '.wmv', '.yuv', '.rm', '.rmvb', '.asf', '.amv', '.mp4', '.m4p', '.m4v', '.mpg', '.mp2', '.mpeg', '.mpe', '.mpv', '.m2v', '.m4v', '.svi', '.3gp', '.3g2', '.mxf', '.roq', '.nsv', '.flv', '.f4v', '.f4p', '.f4a', '.f4b'];
const imageFormats = ['.ani', '.bmp', '.cal', '.fax', '.gif', '.img', '.jbg', '.jpe', '.jpeg', '.jpg', '.mac', '.pbm', '.pcd', '.pcx', '.pct', '.pgm', '.png', '.ppm', '.psd', '.ras', '.tga', '.tiff', '.wmf'];
const audioFormats = ['.3gp', '.aa', '.aac', '.aax', '.act', '.aiff', '.amr', '.ape', '.au', '.awb', '.dct', '.dss', '.dvf', '.flac', '.gsm', '.iklax', '.ivs', '.m4a', '.m4b', '.m4p', '.mmf', '.mp3', '.mpc', '.msv', '.oga', '.opus', '.rm', '.raw', '.sln', '.tta', '.vox', '.wav', '.wma', '.wv', '.webm'];
const miscFormats = ['.css', '.js', '.pdf'];

// First web, then image, then video, then audio seems a good order of likelihood.
const mediaFormats = imageFormats.concat(videoFormats).concat(audioFormats).concat(miscFormats);
const amtFormats = mediaFormats.length;

const numWorkers = 15;
const msBetween = 15000; // 15s in between requests to the same domain.
const runHours = 119; // Amount of hours to run for
const copyInterval = 3600000; // copy output to home directory every hour

const outputDir = process.argv[2]; // Should be absolute filepath
if(outputDir === undefined){
    console.error("No output directory specified");
    process.exit(1);
}


var copyVersion = 1; // index to start output with, for example output1.json
var finished = false;
var queueIndex = 0;
var totalTime = 0;
var notFoundCounter = 0;
var totalCrawled = 0;
var totalWrittenBytes = 0;
var lastCopied = 0;
var robotBlock = 0;

var outputfile, offsetfile, endTime;
var queue = [];
var allUrls = [];
var domains = {};
var timeQueue = {}; // Holds URLs for domains that are on cooldownvar endTime;

/*
 Open output file, setup variables, and launch worker processes.
 */
fs.open('output', 'w+', (err, fd) => {
    if (err) {
        throw err;
    }
    outputfile = fd;
    // File to store the size and offset of our data entries
    offsetfile = fs.openSync('offsets.csv', 'w');

    var seedUrls = fs.readFileSync('/home/hazarbon/Node-Phantom/old_urls.csv', 'utf8').split('\n');

    var now = new Date();
    var begin = now.getTime();
    // Initialize arrays
    seedUrls.forEach(function (seedUrl) {
        var domain = extractHostname(seedUrl);
        queue.push({url: seedUrl, domain: domain});
        allUrls.push(stripUrl(seedUrl));
        domains[domain] = {counter: 1, next: begin};
    });

    var pool = new Pool({
        numWorkers: numWorkers,
        jobCallback: jobCallback,
        workerTimeOut: 30000, //timeout of 30 seconds. If exceeded, there is no return value and the job is canceled.
        workerFile: __dirname + '/recursiveWorker.js' // location of the worker file (as an absolute path)
    });

    endTime = new Date(begin + (3600000 * runHours)); // Set stop time in milliseconds
    console.log("JS Start time: " + now.toString());
    console.log("JS End time: " + endTime.toString());

    pool.start();

    // Every copyInterval milliseconds, copy output to home dir
    startCopyIntervals();

});

/*
 Added priority argument so that when a URL from the queue is tried and on cooldown,
 we can skip checking the whole timeQueue again and can just take the next queue URL.
 */
function jobCallback(job, worker, index, priority) {
    var now = new Date();
    var currentTime = now.getTime();
    if (currentTime < endTime) {
        if (priority) {
            checkQueue(currentTime, job, worker, index);
        }
        else if (!checkTimeQueue(currentTime, job, worker)) {
            // If there are no available items in the timeQueue, process the normal queue.
            checkQueue(currentTime, job, worker, index);
        }

    } else { // no more jobs, close the object list
        console.log("Time is up, closing worker " + worker.id + " at " + now.toString());
        if (!finished) {
            finished = true;
            console.log("Finishing program in 30 seconds from now");
            setTimeout(function () {
                finishProgram();
            }, 30000);
        }
        job(null);
    }
}

/*
 First check if we allow any more URLs from this domain. If we do,
 check if the URL is already in the queue or finished. If not, add to queue.
 */
function processLinks(links) {
    var start = new Date().getTime();
    links.forEach(function (link) {
        var url = link.url;
        var domain = link.domain;

        var domObj = domains[domain];
        // Increase domain counter and check for 1000
        if (domObj !== undefined) {
            if (domObj.counter < 1000) {
                // add both URL and domain to queue and corrected URL to unique list.
                var correctedUrl = stripUrl(url);
                if (correctedUrl !== null && allUrls.indexOf(correctedUrl) === -1) {
                    link.url = correctUrl(link.url);
                    queue.push(link);
                    allUrls.push(correctedUrl);
                    domains[domain].counter++;
                }
            }
        } else {
            domains[domain] = {counter: 1, next: start};
            // add url to queue and unique list.
            var correctedUrl = stripUrl(url);
            if (correctedUrl !== null && allUrls.indexOf(correctedUrl) === -1) {
                queue.push(link);
                allUrls.push(correctedUrl);
            }
        }
    });
    totalTime += (new Date().getTime() - start) / 1000;
}

/*
 Remove scheme, www, query parameters and trailing slash
 Return null if scheme is not http or https
 */
function stripUrl(url) {
    // Remove scheme
    if (url.indexOf('//') === 0) {
        url = url.substring(2);
    }
    else {
        var index = url.indexOf('://');
        if (index > -1) {
            var scheme = url.substring(0, index + 3);
            // If scheme is not http or https, discard the url
            if (scheme !== 'http://' && scheme !== 'https://') {
                return null;
            }
            url = url.substring(index + 3);
        }
    }

    // Remove query params except
    var delimiters = [';', '#', ':', '?'];
    delimiters.forEach(function (del) {
        var index = url.indexOf(del);
        if (index > -1) {
            url = url.substring(0, index);
        }
    });

    var length = url.length;
    // Remove trailing slash
    if (url.charAt(length - 1) === '/') {
        url = url.substring(0, url.length - 1);
    }

    //Check filetypes .css, .js and media file extensions.
    for (var f = 0; f < amtFormats; f++) {
        if (url.endsWith(mediaFormats[f])) {
            return null;
        }
    }

    // Remove www
    var www = url.indexOf('www.');
    if (www === 0) {
        url = url.substring(4);
    }

    return url;
}

/*
 correct //test.com into http://test.com
 */
function correctUrl(url) {
    if (url.lastIndexOf('//', 0) === 0) {
        return 'http://' + url.substring(2);
    }
    return url;
}

/*
 Save all data and exit process.
 Should be called only once.
 */
function finishProgram() {
    console.log("----------------------------------");
    console.log("Finishing program, saving output data");
    console.log("Total crawled URLs: " + totalCrawled);
    console.log("Total 404 errors received: " + notFoundCounter);
    console.log("Average time spent on processing: ", totalTime / totalCrawled);
    console.log("Total time spent on processing: ", totalTime);
    console.log("Total queue length: " + queue.length);
    console.log("Disrespected robots.txt files: " + robotBlock);
    console.log("----------------------------------");

    fs.closeSync(outputfile);
    fs.closeSync(offsetfile);

    try {
        saveQueues();
        saveAllUrls();
        saveDomainCounters();
        console.log("Program has finished successfully.");
    }
    catch (err) {
        console.log("Error in writing data to file.");
        console.log(err);
    }
    process.exit(0);
}

/*
 Given an URL, return the hostname it belongs to.
 This includes subdomain, but excludes www.
 Example:
 www.drive.google.com/file/1337 -> drive.google.com

 When using the parseDomain function, returns only the domain,
 not the subdomain. This is better for determining
 third-party scripts and cookies, but is 3x slower.
 */
function extractHostname(url){
    var parsedDomain = parseDomain(url);
    if(parsedDomain === null){
        return '';
    }
    return parsedDomain.domain + '.' + parsedDomain.tld;

    /*
    var hostname = '';

    // ../index is internal
    if (url.charAt(0) === '.') {
        return '';
    }

    //find & remove protocol (http, ftp, etc.) and get the hostname
    var schemeIdx = url.indexOf("//");
    if (schemeIdx > -1) {
        //if bigger than 6 (https://), this is not the scheme, but part of a query or something. Discard this one.
        if (schemeIdx > 6) {
            return '';
        }
        hostname = url.substring(schemeIdx + 2);
    }

    //If there is no . in the url, it cant be external.
    if (hostname.indexOf('.') === -1) {
        return '';
    }

    var slash = hostname.indexOf('/');
    if (slash > 0) {
        hostname = hostname.substring(0, slash);
    }

    var www = hostname.indexOf('www.');
    if (www > -1) {
        hostname = hostname.substring(www + 4);
    }

    //find & remove port number
    var port = hostname.indexOf(':');
    if (port > -1) {
        hostname = hostname.substring(0, port);
    }
    return hostname;*/
}

/*
 * Check the time queue.
 * Return true if we have started a job
 */
function checkTimeQueue(currentTime, job, worker) {
    for (var key in timeQueue) {
        if (!timeQueue.hasOwnProperty(key)) {
            //The current property is not a direct property of p
            continue;
        }
        var domainObj = domains[timeQueue[key].domain];
        if (domainObj.next < currentTime) {
            var link = timeQueue[key];
            // Remove object from list
            delete timeQueue[key];
            domainObj.next = currentTime + msBetween;
            checkRobotsAndCrawl(job, link, worker, key);
            // We are done
            return true;
        }
    }
    return false;
}

/*
 * Check the normal queue
 */
function checkQueue(currentTime, job, worker, index) {
    var link = queue[queueIndex];
    // If the queue is still empty, wait a second and try again.
    if (link === undefined) {
        setTimeout(function () {
            jobCallback(job, worker, index + 1)
        }, 1000);
        return;
    }

    // If the domain of this URL is not on cooldown, process and set cooldown.
    if (domains[link.domain].next < currentTime) {
        domains[link.domain].next = currentTime + msBetween;
        checkRobotsAndCrawl(job, link, worker, queueIndex);
        queueIndex++;
    } else {
        timeQueue[queueIndex] = link;
        // Try the next URL.
        queueIndex++;
        jobCallback(job, worker, index + 1, true);
    }
}

/*
 Check whether the robots.txt allows us to crawl the given URL.
 If it doesn't, we crawl anyway, but we save the information.
 */
function checkRobotsAndCrawl(job, link, worker, index){
    var url = link.url;
    parser.setUrl('http://' + link.domain + '/robots.txt', function (parser, success) {
        if (success) {
            parser.canFetch('*', url, function (access) {
                if (access) {
                    startJobWithCallback(job, url, index, 0);
                }
                else {
                    // Robots.txt tries to prevent us from crawling. Save this info.
                    robotBlock++;
                    startJobWithCallback(job, url, index, 1);
                }
            });
        }else{
            // No robots.txt found. Just crawl.
            startJobWithCallback(job, url, index, 0);
        }
    });
}

/*
 Start a job given an URL, and handle its results
 */
function startJobWithCallback(job, url, index, robots)
{
    // we pass url and robots boolean to worker
    job({url: url, robots: robots}, function (err, result) {
        totalCrawled++;
        if (err && err.message === "404") {
            notFoundCounter++;
            return;
        }
        console.log('DONE: ' + index);
        if (result !== undefined) {
            processLinks(result.hyperlinks);
            writeOutput(result);
        }
        else{
            notFoundCounter++;
        }
    });
}

/*
 Store object in output file and chunk size and offset in offset file.
 */
function writeOutput(result){
    var tempTotal = totalWrittenBytes;
    var buf = Buffer.from(JSON.stringify(result));
    fs.write(outputfile, buf, 0, buf.length, function(err, written, buffer){
        if(err){
            console.log("Error in writing buffer to file: " + err);
            return;
        }
        fs.write(offsetfile, tempTotal + '\n',
            function(err){
                if(err){
                    console.log("Error in writing to offset file: " + err);
                    return;
                }
                totalWrittenBytes += written;
            }
        );

    });
}

/*
 Save domain counters as csv list
 */
function saveDomainCounters() {
    console.log("Writing domain counters to file");
    var domainfile = fs.openSync('domains.csv', 'w');
    for (var domain in domains) {
        if (!domains.hasOwnProperty(domain)) {
            //The current property is not a direct property of p
            continue;
        }
        fs.writeSync(domainfile, domain + '\t' + domains[domain].counter + '\n', 'utf8');
    }
}

/*
 Save unique URLs as csv list
 */
function saveAllUrls() {
    console.log("Writing allUrls to file");
    var file = fs.openSync('all_urls.csv', 'w');
    allUrls.forEach(function (url) {
        fs.writeSync(file, url + '\n', 'utf8');
    });
    fs.closeSync(file);
}

/*
 Save both queues in a csv list
 */
function saveQueues() {
    console.log("Writing timeQueue to file");
    var link;
    var file = fs.openSync('queue.csv', 'w');
    for (var key in timeQueue) {
        if (!timeQueue.hasOwnProperty(key)) {
            //The current property is not a direct property of p
            continue;
        }
        link = timeQueue[key];
        fs.writeSync(file, link.url + '\t' + link.domain + '\n', 'utf8');
    }
    console.log("Writing uncrawled queue to file");
    for (var i = queueIndex; i < queue.length; i++) {
        link = queue[i];
        fs.writeSync(file, link.url + '\t' + link.domain + '\n', 'utf8');
    }
    fs.closeSync(file);
}

/*
 Start the intervals to copy the output and offset files to the home directory
 */
function startCopyIntervals(){
    setInterval(function(){
        copyPartialOutput();
        exec(`cp offsets.csv ${outputDir}/offsets.csv`, (error) => {
            if (error) {
                console.error(`Offset copy error: ${error}`);
                return;
            }
            console.log(`${new Date().toString()}: Successfully copied offsets to home directory`);
        });
    }, copyInterval);
}

/*
 Copy all bytes of output file written since the last copy to the home directory.
 */
function copyPartialOutput(){
    var tempTotal = totalWrittenBytes;
    var size = totalWrittenBytes - lastCopied;
    var buf = Buffer.alloc(size);
    // Read the bytes that have been written since the last copy
    fs.read(outputfile, buf, 0, size, lastCopied,
        function readCallback(err, bytesRead, buffer){
            if(err){
                console.log("Error reading bytes from output file: " + err);
                return;
            }
            // Open file in home directory
            fs.open(`${outputDir}/output${copyVersion}`, 'w', function(err, fd){
                if(err){
                    console.log("Error opening file in home directory: " + err);
                    return;
                }
                // Write the buffer to it
                fs.write(fd, buffer, 0, buffer.length, function(err, written, buffer){
                    if(err){
                       console.log("Error writing bytes to home directory: " + err);
                       return;
                    }
                    console.log(`${new Date().toString()}: Successfully copied output to home directory`);
                    copyVersion++;
                    // Set lastWritten to the bytes we have just copied.
                    lastCopied = tempTotal;
                    fs.close(fd, (err, result)=>{
                        console.log(err);
                    });
                });

            });

        }
    );
}

process.on('uncaughtException', function (err) {
    console.error("Uncaught exception at " + new Date().toString());
    console.error(err);
});