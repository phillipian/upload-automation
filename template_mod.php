<?php
/**
 * The template part for displaying single posts
 *
 * @package WordPress
 * @subpackage Twenty_Sixteen
 * @since Twenty Sixteen 1.0
 */
?>

<article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
	<header class="entry-header">
		<?php the_title( '<h1 class="entry-title">', '</h1>' ); ?>
	</header><!-- .entry-header -->

	<?php twentysixteen_excerpt(); ?>

	<?php twentysixteen_post_thumbnail(); ?>

	<div class="entry-content">
		<?php
		
		
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
			
		
		
			the_content();

			
		
		
		
			wp_link_pages( array(
				'before'      => '<div class="page-links"><span class="page-links-title">' . __( 'Pages:', 'twentysixteen' ) . '</span>',
				'after'       => '</div>',
				'link_before' => '<span>',
				'link_after'  => '</span>',
				'pagelink'    => '<span class="screen-reader-text">' . __( 'Page', 'twentysixteen' ) . ' </span>%',
				'separator'   => '<span class="screen-reader-text">, </span>',
			) );

			if ( '' !== get_the_author_meta( 'description' ) ) {
				get_template_part( 'template-parts/biography' );
			}
		?>
	</div><!-- .entry-content -->

	<footer class="entry-footer">
		<?php twentysixteen_entry_meta(); ?>
		<?php
			edit_post_link(
				sprintf(
					/* translators: %s: Name of current post */
					__( 'Edit<span class="screen-reader-text"> "%s"</span>', 'twentysixteen' ),
					get_the_title()
				),
				'<span class="edit-link">',
				'</span>'
			);
		?>
	</footer><!-- .entry-footer -->
</article><!-- #post-## -->
