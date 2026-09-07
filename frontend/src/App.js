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
        });
      },
      (error) => {
        // Non-critical: allow app to work without users list
        this.setState({ usersLoaded: true });
      }
    );
  }

  selectUser = (userId) => {
    this.setState({ selectedUserId: userId });
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
                <QuizView
                  users={this.state.users}
                  selectedUserId={this.state.selectedUserId}
                  onSelectUser={this.selectUser}
                />
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
