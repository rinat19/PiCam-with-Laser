$window.keydown(function (event) {
    if (event.keyCode == 37 || event.keyCode == 65) {
        $.ajax({ url: '/left' });
        console.log('left')
    }
    if (event.keyCode == 38 || event.keyCode == 87) {
        $.ajax({ url: '/up' });
        console.log('up')
    }
    if (event.keyCode == 39 || event.keyCode == 68) {
        $.ajax({ url: '/right' });
        console.log('right')
    }
    if (event.keyCode == 40 || event.keyCode == 83) {
        $.ajax({ url: '/down' });
        console.log('down')
    }
    if (event.keyCode == 32) {
        //document.location.href = "http://www.192.168.1.91/add";
         document.location.href = "url: '/add'"
        console.log('laser on/off')
    }
});
