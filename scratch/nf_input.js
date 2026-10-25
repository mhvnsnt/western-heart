<!DOCTYPE html>
<html>
<head>
    <title>Login Redirect</title>
</head>
<body>
    <script>
        window.onload = function() {
            var fragment = window.location.hash;
            var url = new URL('https:\/\/app.netlify.com\/edge-access?domain=endearing-scone-b3d816.netlify.app\u0026requested_path=%2Fjs%2Finput.js\u0026site_id=6e4192c6-a3c2-4499-a169-dff407fd93b8');
            if (fragment) {
                var requestedPath = url.searchParams.get('requested_path');
                url.searchParams.set('requested_path', requestedPath + fragment);
            }
            window.location.href = url.toString();
        };
    </script>

    <noscript>
        <p>Please enable JavaScript to continue. This login redirect requires JavaScript.</p>
    </noscript>
</body>
</html>