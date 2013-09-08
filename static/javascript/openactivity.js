done_callback = null

function checkActivity(callback){
    done_callback = callback
    navigator.geolocation.getCurrentPosition(handleGetCurrentPosition);
}

function handleGetCurrentPosition (location){
    console.log(location.coords);

    $.ajax({
        url: "/api/",
        data: {'lat': location.coords.latitude, 'lng': location.coords.longitude}
        }).done(function(data) {
            done_callback.call(data);
        });

}
