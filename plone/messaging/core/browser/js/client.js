Orbited.settings.port = 9000;
TCPSocket = Orbited.TCPSocket;

(function() { // set up stomp client.
	stomp = new STOMPClient();
	stomp.onconnectedframe = function() {  // Run on initial connection to STOMP (comet) server
		stomp.ready = true;
 		// subscribe to channel CHANNEL = "/ezchat/"
 		var CHANNEL = '/topic/home'
 		stomp.subscribe(CHANNEL);
	};

	stomp.onmessageframe = function(frame) {  // Executed when a messge is received
 		//my_receive( JSON.parse(frame.body) );
		alert(frame.body);
 	};
	
	// Everything is setup. Start the connection!
	stomp.connect(document.domain, 61613); //, 'guest', 'guest');
})();
