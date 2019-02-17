// additions to the content-single.php file 

		
			// added from here
			$attachments = get_children( array(
                        'post_type' => 'attachment',
                        'post_mime_type'=>'image',
                        'numberposts' => -1,
                        'post_status' => 'inherit',
                        'post_parent' => $post->ID
                    )
                );
			if( $attachments ) {
			   foreach ( $attachments as $attachment ) {
// 					echo apply_filters( 'the_title' , $attachment->post_title );
// 					the_attachment_link( $attachment->ID , false );
					?>
		
				   <div class="attachment">
						<?php
					   	echo wp_get_attachment_image( $attachment->ID, $size = 'large');
						echo wp_get_attachment_caption( $attachment->ID );
				   		?>
					</div>
					<?php
			   }
			} else {
			   echo ''; //if no attachment found
			}
			// to here
			
