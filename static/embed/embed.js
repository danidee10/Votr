// Proof of concept, there is absolutely no need to pull in JQuery for this
votr = function(clientId, encodedPollName, embedLocation, height, width) {

    var truncate = `<style>
    .truncate {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    -o-text-overflow: ellipsis;
    -moz-binding: url('assets/xml/ellipsis.xml#ellipsis');
}
</style>
`

    embedLocation = embedLocation.split('/').slice(0,5).join('/');
    var upArrow = embedLocation + '/svg/arrows.svg';
    var downArrow = embedLocation + '/svg/arrows-1.svg';

    /* we aren't doing anything with the client_id yet, but we can use it to know
    if the request is coming from the right source and based on that we can hide/show the poll */

    // Load the script
    var script = document.createElement("script");
    script.src = 'https://code.jquery.com/jquery-2.1.1.min.js';
    script.type = 'text/javascript';
    document.getElementsByTagName("head")[0].appendChild(script);

    // Wait for jQuery to load
    var checkReady = function(callback) {
        if (window.jQuery) {
            callback(jQuery);
        }
        else {
            window.setTimeout(function() { checkReady(callback); }, 100);
        }
    };


    checkReady(function($) {

      var decodedPollName = decodeURI(encodedPollName);
      var pollURL = embedLocation.replace('/static', '') + '/' + encodedPollName;

      var poll = `<div style="position: absolute; bottom: 0px; right:0px; width: ${width}px; padding: 5px;">
                    <div class="truncate" style="width: 96%; background-color: #37474f; padding: 7px;
                      margin-top: 2px; color: white; font-family: Verlag">${decodedPollName}
                        <button id="votr-button" style="float: right; outline: none;
                          padding: 10px; background: none; border: none; background-image:
                          url(${upArrow})">
                        </button>
                    </div>
                    <iframe id="votr-box" src="${pollURL}" height="${height}" width="${width}" frameBorder="0" />
                  </div>`;

      $('body').append(truncate);
      $('body').append(poll);

      $('#votr-button').click(function(){
        $('#votr-box').slideToggle();

        //toggle icon
        if($('#votr-button').css('background-image') == `url("${upArrow}")`){
          $('#votr-button').css('background-image', `url("${downArrow}")`);
        }else {
          $('#votr-button').css('background-image', `url("${upArrow}")`);
        }
      });
    });
};
