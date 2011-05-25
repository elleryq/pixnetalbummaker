/** 
 * Reference:
 * http://blog.realmofzod.com/blog/2009/04/09/asynchronous-image-loading-with-jquery/
 */
var gLoadSpinnerUrl = '/img/ajax-loader.gif';
var gFailImage = '/img/face-surprise.png';

function LoadImage(pSelector, pCallback){
    var loader = $(pSelector);
    loader.html('<img src="' + gLoadSpinnerUrl + '"/>');
 
    LoadThisImage($(img), loader, pCallback);
}

function LoadThisImage(loader, pCallback){
    image_src = loader.attr('src');
    img = new Image();
    $(img).hide();
 
    $(img).load(function() {
        cb_js = loader.get(0).getAttribute('onload');              
        onload_cb = function(){
            eval(cb_js);
        }       
 
        loader.html(this);
        loader.removeClass('loadable-image');
        loader.removeAttr('src');
        loader.removeAttr('onload');
        $(this).show(); 
        if (onload_cb){
            onload_cb($(this));
        }              
        if (pCallback){
            cb = pCallback;
            cb($(this));
        }
    })
    .error(function() { $(this).attr('src', gFailImage).show(); })
    .attr('src', image_src)
    .show();
}

function LoadAllImages( obj ){
    $( '.loadable-image', obj).each(function(){       
        var loader = $(this);
        loader.html('<img src="' + gLoadSpinnerUrl + '"/>');
        LoadThisImage(loader);
    });
}

