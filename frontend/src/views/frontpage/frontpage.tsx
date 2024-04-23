import React from "react";
import "./frontpage.css"
import {Carousel} from "antd";

const FrontPage:React.FC=()=>{
    return(
        <React.Fragment>
            <div className={"frontpage"}>
                <div className={"frontpage-left"}>
                    <div className={"frontpage-left-one"}>
                        <Carousel autoplay className={"carouse"}>
                            <div className={'carouse-div'}>
                                <img src={require('../../assets/img/img1.jpg')} alt="img1" className={'carouse-img'}/>
                            </div>
                            <div className={'carouse-div'}>
                                <img src={require('../../assets/img/img2.jpg')} alt="img2" className={'carouse-img'}/>
                            </div>
                            <div className={'carouse-div'}>
                                <img src={require('../../assets/img/img3.jpg')} alt="img3" className={'carouse-img'}/>
                            </div>
                            <div className={'carouse-div'}>
                                <img src={require('../../assets/img/img4.jpg')} alt="img4" className={'carouse-img'}/>
                            </div>
                            <div className={'carouse-div'}>
                                <img src={require('../../assets/img/img5.jpg')} alt="img5" className={'carouse-img'}/>
                            </div>
                        </Carousel>
                    </div>
                    <div className={"frontpage-left-bottom"}>
                        <div className={"frontpage-left-two"}>
                            <div className="loader">
                                <span></span>
                                <span></span>
                                <span></span>
                                <span></span>
                                <span></span>
                                <span></span>
                                <span></span>
                                <span></span>
                                <span></span>
                                <span></span>
                                <span></span>
                                <span></span>
                                <span></span>
                                <span></span>
                                <span></span>
                            </div>

                        </div>
                        <div className={"frontpage-left-three"}>
                            <img src={require("../../assets/gif/frontpage-right.gif")} alt="frontpage-right-logo" className={"frontpage-right-logo"}/>
                        </div>
                    </div>
                </div>
                <div className={"frontpage-right"} style={{position:"relative"}}>
                    <div id="wrapper">
                        <div id="iphone">
                            <div id="shadow"></div>
                            <div id="side"></div>
                            <div id="lines">
                                <div>
                                    <div>
                                        <div></div>
                                    </div>
                                </div>
                                <div>
                                    <div>
                                        <div></div>
                                    </div>
                                </div>
                            </div>
                            <div id="toggler">
                                <div></div>
                            </div>
                            <div id="aux"></div>
                            <div id="lightning"></div>
                            <div id="bottom-speaker">
                                <div></div>
                                <div></div>
                                <div></div>
                                <div></div>
                                <div></div>
                                <div></div>
                                <div></div>
                            </div>
                            <div id="skrews">
                                <div></div>
                                <div></div>
                            </div>
                            <div id="volume">
                                <div></div>
                                <div></div>
                            </div>
                            <div id="front">
                                <div id="front-cover"></div>
                                <div id="camera">
                                    <div></div>
                                </div>
                                <div id="speaker"></div>
                                <div id="screen">
                                    <div id="reminder">
                                        <div></div>
                                        <div>Made by @_fbrz</div>
                                        <div>now</div>
                                    </div>
                                    <div id="circle"></div>
                                    <div id="time">12:42</div>
                                    <div id="date">Saturday, January 4</div>
                                    <div id="bottom"></div>
                                    <div id="top"></div>
                                    <div id="slide">
                                        <div></div>
                                        slide to unlock
                                    </div>
                                    <div id="signal">
                                        <div></div>
                                        <div></div>
                                        <div></div>
                                        <div></div>
                                        <div></div>
                                    </div>
                                    <div id="battery">
                                        <div>86%</div>
                                        <div>
                                            <div></div>
                                            <div></div>
                                        </div>
                                    </div>
                                </div>
                                <div id="home">
                                    <div></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </React.Fragment>
    )
}
export default FrontPage
