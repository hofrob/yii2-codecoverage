<?php

return (function () {

    $host = getenv('POSTGRES_HOST');
    $db = getenv('POSTGRES_DB');
    $user = getenv('POSTGRES_USER');
    $pass = getenv('POSTGRES_PASSWORD');
    $port = getenv('POSTGRES_PORT');

    return [
        'components' => [
            'db' => [
                'class' => 'yii\db\Connection',
                'dsn' => "pgsql:host=$host;port=$port;dbname=$db",
                'username' => $user,
                'password' => $pass,
                'charset' => 'utf8',
            ],
            'mailer' => [
                'class' => 'yii\swiftmailer\Mailer',
                'viewPath' => '@common/mail',
                // send all mails to a file by default. You have to set
                // 'useFileTransport' to false and configure a transport
                // for the mailer to send real emails.
                'useFileTransport' => true,
            ],
        ],
    ];
})();
