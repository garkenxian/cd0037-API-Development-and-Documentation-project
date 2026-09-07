import React, { Component } from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import './stylesheets/App.css';
import FormView from './components/FormView';
import QuestionView from './components/QuestionView';
import Header from './components/Header';
import QuizView from './components/QuizView';
import { apiGet } from './utils/api';

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      users: [],
      selectedUserId: null,
      usersLoaded: false,
      usersLoadError: null,
    };
  }

  componentDidMount() {
    // Load available users for game play
    apiGet(
      '/users',
      (result) => {
        this.setState({
          users: result.users || [],
          usersLoaded: true,
          usersLoadError: null,
        });
      },
      (error) => {
        // Track error but allow app to work without users list
        this.setState({ 
          usersLoaded: true,
          usersLoadError: error || 'Failed to load users',
        });
      }
    );
  }

  selectUser = (userId) => {
    this.setState({ selectedUserId: userId });
  };

  refreshUsers = (callback) => {
    // Fetch updated users list and call callback when complete
    apiGet(
      '/users',
      (result) => {
        this.setState({
          users: result.users || [],
          usersLoaded: true,
          usersLoadError: null,
        }, callback);
      },
      (error) => {
        this.setState({ 
          usersLoaded: true,
          usersLoadError: error || 'Failed to load users',
        }, callback);
      }
    );
  };

  render() {
    return (
      <div className='App'>
        <Header path />
        <Router>
          <Switch>
            <Route path='/' exact component={QuestionView} />
            <Route path='/add' component={FormView} />
            <Route 
              path='/play' 
              render={() => (
                <div>
                  {!this.state.usersLoaded && (
                    <div className='loading-message'>
                      Loading users...
                    </div>
                  )}
                  {this.state.usersLoaded && this.state.usersLoadError && (
                    <div className='error-message'>
                      {this.state.usersLoadError}
                    </div>
                  )}
                  {this.state.usersLoaded && !this.state.usersLoadError && (
                    <QuizView
                      users={this.state.users}
                      selectedUserId={this.state.selectedUserId}
                      onSelectUser={this.selectUser}
                      onUsersRefresh={this.refreshUsers}
                    />
                  )}
                </div>
              )}
            />
            <Route component={QuestionView} />
          </Switch>
        </Router>
      </div>
    );
  }
}

export default App;
