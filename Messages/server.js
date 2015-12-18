var WebSocketServer = require('ws').Server;
var wss = new WebSocketServer({ port: 80 });

var channels = {};
var url_req = /^\/(\d+)$/;
wss.on('connection', function(ws) {
    var matched = client.upgradeReq.url.match(url_req);
    if (!matched) {
        ws.close();
        return;
    }

    var proposal_id = matched[1];
    if (!(proposal_id in channels)) {
        channels[proposal_id] = [];
    }
    channels[proposal_id].push(ws);

    ws.on('message', function(message)) {
        spreadMessage(proposal_id, ws, message);
    });
    ws.on('close', function() {
        var clients = channels[proposal_id];
        var index = clients.indexOf(ws);
        clients.splice(index, 1);
        if (clients.length === 0) {
            delete channels[proposal_id];
        }
    });
});

function spreadMessage(proposal_id, sender, message) {
    var clients = channels[proposal_id];
    for (var i = 0; i < clients.length; i++) {
        if (clients[i] !== sender) clients[i].send(message);
    }
}
