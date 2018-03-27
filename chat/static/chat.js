$(function() {
  var conn = null;
  var name = "UNKNOWN";
  var wsProto = (window.location.protocol == 'https:' && 'wss://' || 'ws://');

  function log(msg) {
    var control = $('#log');
    control.html(control.html() + msg + '<br/>');
    control.scrollTop(control.scrollTop() + 1000);
  }

  function connect() {
    disconnect();
    update_messages();
    conn = new WebSocket(wsProto + window.location.host + '/ws' + window.location.pathname);
    log('Connecting...');
    conn.onopen = function() {
      log('Connected.');
      update_ui();
    };
    conn.onmessage = function(e) {
      var data = JSON.parse(e.data);
      switch (data.action) {
        case 'connect':
          name = data.name;
          log('Connected as ' + name);
          update_ui();
          break;
        case 'disconnect':
          name = data.name;
          log('Disconnected ' + name);
          update_ui();
          break;
        case 'join':
          log('Joined ' + data.name);
          break;
        case 'sent':
          log(data.name + ': ' + data.text);
          break;
      }
    };
    conn.onclose = function() {
      log('Disconnected.');
      conn = null;
      update_ui();
    };
  }

  function disconnect() {
    if (conn != null) {
      log('Disconnecting...');
      conn.close();
      conn = null;
      name = 'UNKNOWN';
      update_ui();
    }
  }

  function update_messages() {
      var xhr = new XMLHttpRequest();
      xhr.open('get', '/last_messages' + window.location.pathname);
      xhr.onload = function (e) {
        var messages = JSON.parse(xhr.response);
        messages.forEach(function (value) {
          if (value.msg.text){
            log(value.msg.name + ': ' + value.msg.text);
          }
        })
      };
      xhr.send();
  }

  function update_ui() {
    if (conn == null) {
      $('#status').text('disconnected');
      $('#connect').html('Connect');
    } else {
      $('#status').text('connected (' + conn.protocol + ')');
      $('#connect').html('Disconnect');
    }
    $('#name').text(name);
  }

  $('#connect').on('click', function() {
    if (conn == null) {
      connect();
    } else {
      disconnect();
    }
    update_ui();
    return false;
  });
  $('#send').on('click', function() {
    var text = $('#text').val();
    log('Sending: ' + text);
    conn.send(text);
    $('#text').val('').focus();
    return false;
  });
  $('#text').on('keyup', function(e) {
    if (e.keyCode === 13) {
      $('#send').click();
      return false;
    }
  });
});