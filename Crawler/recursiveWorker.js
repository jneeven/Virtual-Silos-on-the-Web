const webpage = require('webpage');
const xpath = require('xpath');
const DOM = require('xmldom').DOMParser;
const parseDomain = require('parse-domain');

phantom.cookiesEnabled = true;
phantom.onError = onPhantomError;

module.exports = function(data, done, worker) {
    crawlPage(data, done);
};

function crawlPage(data, done){
    var url = data.url;
    var cookies = [];
    var domain = extractHostname(url);
    var amtErrors = 0;
    var links = [];

    var page = webpage.create();
    page.settings.userAgent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0';
    page.settings.resourceTimeout = 15000; //we want a 30s timeout, but it misbehaves on the cluster.
    //Setting it to 15s should hopefully roughly approach 30s.
    page.settings.loadImages = false;
    page.onResourceTimeout = onTimeout;

    // We do not handle javascript errors, because we do not influence the executed
    // code. Therefore, just add 1 to the error counter and continue.
    page.onError = function onPageError(error){
        amtErrors += 1;
    };

    page.onResourceReceived = function checkCookies(response){
        if(response.status === 404){
            done(new Error("404"), undefined);
            return;
        }

        // Only parse third-party requests
        var srcHost = extractHostname(response.url);
        if(srcHost == domain || srcHost == '') return;
        // check if the resource is done downloading
        if (response.stage !== "end") return;
        for (var i = 0; i < response.headers.length; i++) {
            if (response.headers[i].name.toLowerCase() == 'set-cookie') {
                cookies.push(correctUrl(response.url));
                return true;
            }
        }
    };

    page.open(url, function (status) {
        var scripts = [];

        var doc = new DOM({
            errorHandler: {
                warning: null,
                error: null,
                fatalError: fatalDOMError
            }
        }).parseFromString(page.content);

        // get third party scripts
        var nodes = xpath.select('//script/@src', doc);
        for(var i = 0; i < nodes.length; i++){
            var src = nodes[i].value.toString();
            var srcHost = extractHostname(src);
            if(src && srcHost != domain && srcHost != ''){
                scripts.push(correctUrl(src));
            }
        }

        // Count internal and external links
        var internal = 0;
        var external = 0;
        nodes = xpath.select('//a/@href', doc);
        for(var i = 0; i < nodes.length; i++){
            var link = nodes[i].value.toString();
            var hostname = extractHostname(link);
            if(hostname == domain || hostname == ''){
                internal++;
            }
            else{
                links.push({url: link, domain: hostname});
                external++;
            }
        }
        page.close();
        done(null, {url: url, scripts: scripts, cookies: cookies,
            amtErrors: amtErrors, links: [internal, external], domain: domain,
            hyperlinks: links, robots: data.robots});
    });
}

function extractHostname(url) {
    var parsedDomain = parseDomain(url);
    if(parsedDomain === null){
        return '';
    }
    return parsedDomain.domain + '.' + parsedDomain.tld;

    /*
    var hostname = '';

    // ../index is internal
    if(url.charAt(0) === '.'){
        return '';
    }

    //find & remove protocol (http, ftp, etc.) and get the hostname
    var schemeIdx = url.indexOf("//");
    if (schemeIdx > -1) {
        //if bigger than 6 (https://), this is not the scheme, but part of a query or something. Discard this one.
        if(schemeIdx > 6){
            return '';
        }
        hostname = url.substring(schemeIdx + 2);
    }

    //If there is no . in the url, it cant be external.
    if(hostname.indexOf('.') === -1){
        return '';
    }

    var slash = hostname.indexOf('/');
    if(slash > 0){
        hostname = hostname.substring(0, slash);
    }

    var www = hostname.indexOf('www.');
    if(www > -1){
        hostname = hostname.substring(www + 4);
    }

    //find & remove port number
    var port = hostname.indexOf(':');
    if(port > -1){
        hostname = hostname.substring(0, port);
    }
    return hostname;*/
}

// Remove scheme, www, query parameters and trailing slash
function correctUrl(url) {
    // Remove scheme
    if (url.indexOf('//') === 0) {
        url = url.substring(2);
    }
    else{
        var index = url.indexOf('://');
        if(index > -1){
            url = url.substring(index + 3);
        }
    }

    // Remove query params except
    var delimiters = [';', '#', ':', '?'];
    delimiters.forEach(function(del){
       var index = url.indexOf(del);
       if (index > -1){
           url = url.substring(0, index);
       }
    });

    // Remove trailing slash
    if(url.charAt(url.length - 1) == '/'){
        url = url.substring(0, url.length - 1);
    }

    // Remove www
    var www = url.indexOf('www.');
    if(www === 0){
        url = url.substring(4);
    }
    return url;
}

function fatalDOMError(error){
    console.error(JSON.stringify({error: "FATAL DOM ERROR: " + error}));
}

function onTimeout() {
    return;
}

function onPhantomError(error){
    console.error(JSON.stringify({error: "caught a phantom error: " + error}));
}