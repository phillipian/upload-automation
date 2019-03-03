<div class="entry-content">
    <!-- Add the attachments -->
    <?php
        $images =& get_children( array (
            'post_parent' => $post->ID,
            'post_type' => 'attachment',
            'post_mime_type' => 'image'
        ));

        if ( empty($images) ) {
            // no attachments here
        } else {
            foreach ( $images as $attachment_id => $attachment ) {
                $caption = wp_get_attachment_caption($attachment_id);
                $credit = get_post($attachment_id)->post_content;
                $width = wp_get_attachment_metadata($attachment_id)['sizes']['medium']['width'];

                $img_style = ['style' => 'display:block;margin: 0 auto;'];
                $img_markdown = wp_get_attachment_image($attachment_id, 'medium', false, $img_style);

                if ($credit != '')
                {
                    $img_markdown = '[media-credit align="aligncenter" name=' . "\"$credit\"" . 
                        " width=\"$width\"]" . $img_markdown . '[/media-credit]';
                }

                if ($caption != '')
                {
                    $img_markdown = "[caption align=\"aligncenter\" width=\"$width\"]" . 
                        $img_markdown . "$caption [/caption]";
                }

                $img_html = do_shortcode($img_markdown);
                echo $img_html;
            }
        }
    ?>

    <!-- The remainder of the entry-content goes here! -->
</div>
