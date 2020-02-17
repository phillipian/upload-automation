<?php

/*
To use: php -f assign_media_credit.php [image post id] [corresponding main post id] "[media credit]"
(media credit is enclosed in quotes)
*/

require_once("/home/plipdigital/phillipian.net/wp-load.php");
require_once("/home/plipdigital/phillipian.net/wp-admin/includes/media.php");
require_once("/home/plipdigital/phillipian.net/wp-content/plugins/media-credit/includes/media-credit/class-core.php");

use Media_Credit\Core;

$post_id = $argv[1];
$post_parent_id = $argv[2];
$media_credit = $argv[3];

$user = get_user_by_name($media_credit);

//To debug media credit value, use attachment_fields:
$attachment_fields = get_attachment_fields_to_edit(get_post($post_id), $errors = null ); 

$post = get_post($post_id);

// Update media credit
if ($user == null) {
    $fields = array ('freeform' => $media_credit);
} else {
    $user_info = get_userdata($user->ID);
    $user_display = $user_info->display_name;
    $user_login = $user_info->user_login;
    echo("Assigning credit to user with name " . $user_display . " and id " . $user->ID . " (login " . $user_login . ")\n");
    $fields = array ('freeform' => $user_display, 'user_id' => $user->ID);
}
Core::get_instance()->update_media_credit_json($post, $fields);

$media_post = wp_update_post( array(
    'ID'            => $post_id,
    'post_parent'   => $post_parent_id,
), true );

if( is_wp_error( $media_post ) ) {
    error_log( print_r( $media_post, 1 ) );
}

function get_user_by_name($name) {
    $search_string = esc_attr( trim( get_query_var('s') ) );
    $users = new WP_User_Query( array(
        'search'         => '*'.esc_attr( $name ).'*',
	'search_columns' => array(
	    'display_name'
	),
    ));
    $users_found = $users->get_results();

    if ($users_found == null) {
	echo("No user found for " . $name . ", cannot link image to author page!\n");
	return null;
    }

    return $users_found[0];
}

?>
