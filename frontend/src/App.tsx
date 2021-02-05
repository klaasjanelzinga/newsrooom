import * as React from 'react';
import {createStyles, WithStyles, withStyles} from "@material-ui/core";
import './App.css';
import {Api} from "./Api"
import {withSnackbar, WithSnackbarProps} from "notistack";
import {RouteComponentProps} from "react-router";
import News, {NewsVariant} from "./news/news";
import {withRouter} from "react-router-dom";
import {WithAuthHandling, withAuthHandling} from "./WithAuthHandling";

const styles = createStyles({})

interface AppProps extends RouteComponentProps, WithSnackbarProps, WithAuthHandling, WithStyles<typeof styles> {
}

class App extends React.Component<AppProps> {

    apiFetch: Api

    constructor(props: AppProps) {
        super(props);
        this.apiFetch = new Api(this.props)
    }

    render() {
        return <div>
            <News variant={NewsVariant.NEWS}/>
        </div>
    }
}

export default withStyles(styles)(withRouter(withSnackbar(withAuthHandling(App))))
