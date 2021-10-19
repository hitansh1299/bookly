def prepare_div(ad: (str, str, str, str, str, str, str, float, str, str)) -> str:
    return (
        f'''<div class="col-xl-4 col-lg-12 col-md-12 col-sm-12 col-12 margin_10px">
                    <div class="post-box">
                        <div class="thumbnail-holder">
                            <a href="product.html?id={ad[9]}">
                                        <img src="img/logo_200x200.png" alt="{ad[0]}">
                            </a>
                        </div>
                    <div class="post-box-content">
                        <h3><a href="product.html?id={ad[9]}">{ad[0]}</a></h3>

                        <div class="post-category">
                            <a href="#"> <i class="fa fa-list-alt"></i> {ad[1]}</a>
                        </div>

                        <div class="post-location">
                            <a href="#"> <i class="fa fa-location-arrow"></i> {ad[3]}</a>
                        </div>

                        <div class="post-meta">
                            <i class="fa fa-dollar"></i>{ad[7]}
                        </div>
                        <div class="clearfix"></div>
                    </div>
                </div>
            </div>
            '''
    )
