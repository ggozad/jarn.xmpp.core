var BOSH_SERVICE = 'http://localhost:8080/http-bind/'
var connection = null;

function onConnect(status)
{
}

$(document).ready(function () {
    connection = new Strophe.Connection(BOSH_SERVICE);
	connection.connect('admin@localhost', 'admin', onConnect);
});