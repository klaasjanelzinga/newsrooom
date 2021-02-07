import {Avatar, createStyles, IconButton, Menu, MenuItem, WithStyles} from '@material-ui/core';
import {withStyles} from '@material-ui/core/styles';
import {AccountCircle} from '@material-ui/icons';
import React from 'react';
import {RouteComponentProps, withRouter} from 'react-router-dom';
import {withAuthHandling, WithAuthHandling} from "../WithAuthHandling";
import {Api} from "../Api";
import {withSnackbar, WithSnackbarProps} from "notistack";

const styles = createStyles({});

interface UserAvatarResponse {
    avatar_image: string | null;
}

interface HeaderMenuProps extends RouteComponentProps, WithAuthHandling, WithSnackbarProps, WithStyles<typeof styles> {
}

type HeaderMenuState = {
    anchorEl: null | HTMLElement;
    menuOpen: boolean;
    avatar_image: string | null;
}

class HeaderMenu extends React.Component<HeaderMenuProps, HeaderMenuState> {

    api: Api

    constructor(props: HeaderMenuProps) {
        super(props);
        this.api = new Api(props)
        this.state = {
            anchorEl: null,
            menuOpen: false,
            avatar_image: this.props.authHandling.user_information?.avatar_image || null,
        };

        this.fetch_avatar_image()
    }

    fetch_avatar_image() {
        if (this.state.avatar_image) {
            return
        }
        this.api.get<UserAvatarResponse>("/user/avatar")
            .then(user_avatar_response => {
                if (user_avatar_response[0] === 200) {
                    this.setState({avatar_image: user_avatar_response[1].avatar_image})
                    this.props.authHandling.update_avatar_image(user_avatar_response[1].avatar_image)
                }
            })
            .catch(reason => console.log(reason))
    }

    handleMenu = (event: React.MouseEvent<HTMLElement>):void => {
        this.setState({
            anchorEl: event.currentTarget,
            menuOpen: true,
        });
    }

    handleClose = () => {
        this.setState({
            menuOpen: false,
            anchorEl: null,
        });
    }

    handleSignIn = () => {
        this.handleClose();
        this.props.history.push('/user/signin');
    }

    handleSignOut = () => {
        this.handleClose();
        this.props.history.push('/user/signout');
    }

    handleMyProfile = () => {
        this.handleClose();
        this.props.history.push('/user/profile');
    }

    handleChangePassword = () => {
        this.handleClose();
        this.props.history.push('/user/change-password');
    }

    accountAvatar = () => {
        if (this.state.avatar_image) {
            return <Avatar src={this.state.avatar_image}
                           alt={this.props.authHandling.user_information?.display_name || "?"}/>
        }
        return <AccountCircle />
    }

    render() {
        return (
            <div>
                <IconButton
                    aria-label="Account of current user"
                    aria-controls="menu-appbar"
                    aria-haspopup="true"
                    onClick={this.handleMenu}
                    color="inherit">
                    {this.accountAvatar()}
                </IconButton>
                <Menu
                    id="menu-appbar"
                    anchorEl={this.state.anchorEl}
                    keepMounted
                    open={this.state.menuOpen}
                    onClose={this.handleClose}>
                    <MenuItem disabled={this.props.authHandling.isSignedIn} onClick={this.handleSignIn}>Sign in</MenuItem>
                    <MenuItem disabled={!this.props.authHandling.isSignedIn} onClick={this.handleMyProfile}>Profile</MenuItem>
                    <MenuItem disabled={!this.props.authHandling.isSignedIn} onClick={this.handleSignOut}>Sign out</MenuItem>
                    <MenuItem onClick={this.handleChangePassword}>Change password</MenuItem>
                </Menu>
            </div>
        );
    }
}

export default withStyles(styles)(withRouter(withAuthHandling(withSnackbar(HeaderMenu))))
