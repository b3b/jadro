/*

Ajax Android RPC

     Usage

// just call
for (i=0; i < 4; i++) {
    droid('makeToast', i);
}

// handle result, and error
droid('makeRoast').error(function(e) {
    alert('Error: ' + e.error + '\nhmmm'); });

droid('dialogGetInput', 'Say What Again!', '', 'What??').result(function(r) {
    droid('ttsSpeak', r.result);}).error(function() {
    alert('Error');});


// sequential handlers
var r = droid('getRunningPackages');
r.result(function() {
    $('body').append("<h1>Running Packages</h1><ul id='Packages'></ul>");
});
r.result(function(packages){
    $.each(packages.result, function() {
        $('#Packages').append('<li>' + String(this) + '</li>');)});
*/

var droid = function(method) {
    if (arguments.length) {
        var params = [];
        for (var i = 1; i < arguments.length; i++) {
            params.push(arguments[i]);
        }
        return new AndroidRPC().rpc(method, params);
    }
};

AndroidRPC = function() {};
AndroidRPC.prototype = {    
    rpc: function(method, params) {
        var data = {method: method};
        var result = new rpcResult();
        $.each(params, function(i, v){
            data['par' + (i + 1).toString()] = v;
        });
        if (AndroidRPC._token === undefined) { // first call
            AndroidRPC._token = '';
            // handshake
            this._enqueue({type: 'GET', data: {}, success: function(data) {
                if (data.csrfmiddlewaretoken === undefined) {
                    throw 'Bad handshake';
                }                
                AndroidRPC._token = data.csrfmiddlewaretoken;
                return true;
            }});
        }
        this._enqueue({type: 'POST', data: data, success: function(data) {
            var data = data.result;
            if (data.length != 3) {
                throw 'Bad call result';
            }
            var data = {
                call_id: data[0], 
                result: data[1],
                error: data[2]
            };
            if (data.error) {
                result.error = data;
            } else {
                result.result = data;
            }
            return true;
        }});
        return result;
    },
     _enqueue: function(opts) {
        var success = opts.success;
        opts.url = AndroidRPC.droid_url;
        AndroidRPC._ajax_queue.queue(function(next) {
            if (AndroidRPC._token) {
                opts.data.csrfmiddlewaretoken = AndroidRPC._token;
            }
            opts.success = function(data) { // on Ajax success
                var allow_next = true;
                if (success) {
                    allow_next = success(data); // execute success handler
                }
                if (allow_next) {
                    next(); // call the next procedure from the queue
                } // else - stop future calls
            };
            $.ajax(opts);
        });
    }
};

AndroidRPC.droid_url = '/droid/api/'; // hardcoded
AndroidRPC._ajax_queue = $({});

var rpcResult = function() {
    this._data = {},
    this._handlers = {
        result: [],
        error: [],
    };
};

rpcResult.prototype = {
    _get: function(key) {
        return function(handler) {
            if (key in this._data) { // got data already
                handler(this._data[key]);
            } else {
                this._handlers[key].push(handler); // register handler
            }
            return this;
        };
    },
    _set: function(key, val) {
        this._data[key] = val;
        // run registered handlers in order, clean the registry
        while (this._handlers[key].length) {
            var handler = this._handlers[key].shift();
            handler(val);
        }
        return this;
    },
    get result() {
        return this._get('result');
    },
    set result(val) {
        return this._set('result', val);
    },
    get error() {
        return this._get('error');
    },
    set error(val) {
        return this._set('error', val);
    }
};
