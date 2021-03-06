import * as React from "react"
import { Button, Card, CardContent, createStyles, Typography, WithStyles, withStyles } from "@material-ui/core"
import { withSnackbar, WithSnackbarProps } from "notistack"
import { RouteComponentProps, withRouter } from "react-router-dom"
import HeaderBar from "../headerbar/HeaderBar"
import { Api } from "../Api"
import { TokenBasedAuthenticator, withAuthHandling, WithAuthHandling } from "../WithAuthHandling"
import Grid from "@material-ui/core/Grid"
import TextField from "@material-ui/core/TextField"
import LockIcon from "@material-ui/icons/Lock"

const styles = createStyles({
    card: {
        display: "flex",
        width: "600px",
        margin: "10px",
    },
    cards: {
        padding: "10px",
        width: "100%",
    },
    saveButton: {
        marginLeft: "8px",
    },
    signUpButton: {
        marginLeft: "8px",
    },
    buttonBar: {
        fontSize: "13px",
        backgroundColor: "lightgrey",
        padding: "8px",
        marginTop: "20px",
    },
    errorMessage: {
        color: "red",
    },
})

interface ChangePasswordAttrs
    extends WithAuthHandling,
        WithStyles<typeof styles>,
        RouteComponentProps,
        WithSnackbarProps {}

interface ChangePasswordState {
    email_address: string
    current_password: string
    new_password: string
    new_password_repeated: string
    error_message: string
}

class ChangePassword extends React.Component<ChangePasswordAttrs, ChangePasswordState> {
    apiFetch: Api
    authHandling: TokenBasedAuthenticator

    constructor(props: ChangePasswordAttrs) {
        super(props)
        this.apiFetch = new Api(props)
        this.authHandling = props.authHandling
        this.state = {
            email_address: this.props.authHandling.user_information?.email_address || "",
            current_password: "",
            new_password: "",
            new_password_repeated: "",
            error_message: "",
        }
    }

    async change_password(): Promise<void> {
        try {
            const sign_in_result = await this.authHandling.change_password(
                this.state.email_address,
                this.state.current_password,
                this.state.new_password,
                this.state.new_password_repeated
            )
            if (!sign_in_result.success) {
                this.setState({ error_message: sign_in_result.reason || "" })
            } else {
                await this.authHandling.sign_out()
                this.props.enqueueSnackbar(`Changing of password succeeded. Please sign in again`, {
                    variant: "info",
                    autoHideDuration: 3000,
                })
                this.props.history.push("/user/signin")
            }
        } catch (error) {
            this.props.enqueueSnackbar("Cannot sign in", {
                variant: "warning",
                autoHideDuration: 3000,
            })
        }
        return Promise.resolve()
    }

    render(): JSX.Element {
        const { classes } = this.props
        return (
            <div>
                <HeaderBar />

                <div className={classes.cards}>
                    <Card className={classes.card}>
                        <CardContent>
                            <Grid container>
                                <Grid item xs={12}>
                                    <Typography component="h5" variant="h5">
                                        Change your password for newsroom:
                                    </Typography>
                                </Grid>
                                <Grid item xs={12}>
                                    <TextField
                                        required
                                        id="email"
                                        name="email"
                                        label="Email address"
                                        fullWidth
                                        onChange={(e): void => this.setState({ email_address: e.currentTarget.value })}
                                        value={this.state.email_address}
                                        autoComplete="username"
                                    />
                                </Grid>
                                <Grid item xs={12}>
                                    <TextField
                                        required
                                        id="password"
                                        name="password"
                                        label="Current password"
                                        type="password"
                                        onChange={(e): void =>
                                            this.setState({ current_password: e.currentTarget.value })
                                        }
                                        value={this.state.current_password}
                                        fullWidth
                                        autoComplete="current-password"
                                    />
                                </Grid>
                                <Grid item xs={12}>
                                    <TextField
                                        required
                                        id="new_password"
                                        name="password"
                                        label="New password"
                                        type="password"
                                        onChange={(e): void => this.setState({ new_password: e.currentTarget.value })}
                                        value={this.state.new_password}
                                        fullWidth
                                        autoComplete="new-password"
                                    />
                                </Grid>
                                <Grid item xs={12}>
                                    <TextField
                                        required
                                        id="new_repeated_password"
                                        name="new_repeated_password"
                                        label="Repeat password"
                                        type="password"
                                        onChange={(e): void =>
                                            this.setState({ new_password_repeated: e.currentTarget.value })
                                        }
                                        value={this.state.new_password_repeated}
                                        fullWidth
                                        autoComplete="new-password"
                                    />
                                </Grid>
                                <Grid item xs={12}>
                                    {this.state.error_message && (
                                        <Typography>
                                            <div className={classes.errorMessage}>{this.state.error_message}</div>
                                        </Typography>
                                    )}
                                </Grid>
                                <Grid item xs={12}>
                                    <div className={classes.buttonBar}>
                                        <Button
                                            variant="contained"
                                            color="primary"
                                            className={classes.saveButton}
                                            onClick={async (): Promise<void> => await this.change_password()}
                                        >
                                            Change password
                                            <LockIcon />
                                        </Button>
                                    </div>
                                </Grid>
                            </Grid>
                        </CardContent>
                    </Card>
                </div>
            </div>
        )
    }
}

export default withStyles(styles)(withRouter(withSnackbar(withAuthHandling(ChangePassword))))
