var Router = ReactRouter.Router;
var Route = ReactRouter.Route;
var browserHistory = ReactRouter.browserHistory
try {
  var SimpleTimePicker = ReactSimpleTimePicker.SimpleTimePicker;
}catch(err){
  console.log(err);
}

// css style to align text to the center of it's container
var Align = {
  textAlign: 'center',
  fontFamily: 'EB Garamond'
};

var TimeLeft = {
  color: '#999',
  fontSize: '15px'
}

//global variable to store origin url (e.g http://localhost:5000)
var origin = window.location.origin;

var PollForm = React.createClass({

  getInitialState: function(e){
    // set initial state of form inputs

    // close poll in 24 hours by default
    var close_date = new Date();
    close_date.setHours(close_date.getHours() + 24);
    close_date = close_date.getTime() / 1000;


    return {title: '', option: '', options: [], close_date: close_date, all_options: []}
  },

  handleTitleChange: function(e){
    //change title as the user types
    this.setState({title: e.target.value});
  },

  handleOptionChange: function(e){
    this.setState({option: e.target.value});
  },

  handleOptionAdd: function(e){
    //update poll options and reset options to an empty string
    this.setState({
    options: this.state.options.concat({name: this.state.option}),
    option: ''
    });
  },

  onDateChange: function(e){
    // convert date to UTC timestamp in seconds
    var close_date = e.getTime() / 1000

    this.setState({close_date: close_date})
  },

  componentDidMount: function(){

    var url =  origin + '/api/polls/options'

    //get all options
    $.ajax({
      url: url,
      dataType: 'json',
      cache: false,
      success: function(data) {
        this.setState({all_options: data});
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(url, status, err.toString());
      }.bind(this)
    });

  },

  handleSubmit: function(e){
    e.preventDefault();
    var title = this.state.title;
    var options = this.state.options;
    var close_date = this.state.close_date;

    var data = {title: title,
                options: options.map(function(x){return x.name}),
                close_date: close_date
              };

    var url =  origin + '/api/polls'

    // make post request
    $.ajax({
      url: url,
      dataType: 'json',
      type: 'POST',
      data: JSON.stringify(data),
      contentType: 'application/json; charset=utf-8',
      success: function(data){
        alert(data.message);
      }.bind(this),
      error: function(xhr, status, err){
        alert('Poll creation failed: ' + err.toString());
      }.bind(this)
    });
  },

  render: function(){

    var classContext = "col-sm-6 col-sm-offset-3"

    var all_options = this.state.all_options.map(function(option){
                        return(<option key={option.id} value={option.name} />)
                      });

    return (
    <div>
      <form id="poll_form" className="form-signin" onSubmit={this.handleSubmit}>
        <h2 className="form-signin-heading" style={Align}>Create a poll</h2>

        <div className="form-group has-success">
          <label htmlFor="title" className="sr-only">Title</label>
          <input type="text" id="title" name="title" className="form-control" placeholder="Title" onChange={this.handleTitleChange} required autoFocus />
        </div>

        <div className="form-group has-success">
          <label htmlFor="option" className="sr-only">Option</label>
          <input list="option" className="form-control" placeholder="Option" onChange={this.handleOptionChange}
          value={this.state.option ? this.state.option: ''} autoFocus />
        </div>

        <datalist id="option">
          {all_options}
        </datalist>


        <SimpleTimePicker days="7" onChange={this.onDateChange} />
        <br />

        <div className="row form-group">
          <button className="btn btn-lg btn-success btn-block" type="button" onClick={this.handleOptionAdd}>Add option</button>
          <button className="btn btn-lg btn-success btn-block" type="submit">Save poll</button>
        </div>
        <br />
      </form>

      <div className="row">
      <h3 style={Align}>Live Preview</h3>
        <LivePreview title={this.state.title} options={this.state.options} classContext={classContext} />
      </div>
    </div>
    );
  }
});

var LivePreview = React.createClass({

  getInitialState: function(){
    return {selected_option: '', disabled: 0};
  },

  handleOptionChange: function(e){
    this.setState({selected_option: e.target.value });
  },


  voteHandler: function(e){
    e.preventDefault();

    var data = {"poll_title": this.props.title, "option": this.state.selected_option};

    //calls props handler
    this.props.voteHandler(data);

    //disable the button
    this.setState({disabled: 1});

  },

  render: function(){
    var options = this.props.options.map(function(option){

      if(option.name) {

        // calculate progress bar percentage
        var progress = Math.round((option.vote_count / this.props.total_vote_count) * 100) || 0
        var current = {width: progress+"%"}

        return (
          <div key={option.name}>
            <input name="options" type="radio" value={option.name} onChange={this.handleOptionChange} /> {option.name}
            <div className="progress">
              <div className="progress-bar progress-bar-success" role="progressbar" aria-valuenow={progress}
              aria-valuemin="0" aria-valuemax="100" style={current}>
                {progress}%
              </div>
            </div>
          </div>
        );
      }
    }.bind(this));

    return(

      <div className={this.props.classContext}>
        <div className="panel panel-success">
          <div className="panel-heading">
            <h4>{this.props.title}</h4>
          </div>
          <div className="panel-body">
            <form onSubmit={this.voteHandler}>
              {options}
              <br />
              <button type="submit" disabled={this.state.disabled}
              className="btn btn-success btn-outline hvr-grow">Vote!</button>
              <small> {this.props.total_vote_count} votes so far</small>
              <small style={TimeLeft}> | {this.props.close_date}</small>
            </form>
          </div>
        </div>
      </div>
    )
  }
});


var LivePreviewProps = React.createClass({

  voteHandler: function(data){

    var url =  origin + '/api/poll/vote'

    // make patch request
    $.ajax({
      url: url,
      dataType: 'json',
      type: 'PATCH',
      data: JSON.stringify(data),
      contentType: 'application/json; charset=utf-8',
      success: function(data){
        alert(data.message);
        this.setState({selected_option: ''});
        this.props.loadPollsFromServer();
      }.bind(this),
      error: function(xhr, status, err){
        alert('Poll creation failed: ' + err.toString());
      }.bind(this)
    });

  },


  render: function(){
    var polls = this.props.polls.Polls.map(function(poll){

      var minutes = Math.floor((Date.parse(poll.close_date) - Date.now()) / (60000));
      var time_remaining = '';

      if(minutes > 1 && minutes < 59){
        time_remaining += minutes + ' minutes remaining';
      }

      else if(minutes < 1380){
        var hours =  Math.floor(minutes / 60);
        time_remaining += hours + ' hours remaining';
      }

      else {
        var days = Math.floor(minutes / (24 * 60));
        time_remaining += days + ' days remaining';
      }

      return (
        <LivePreview key={poll.title} title={poll.title} options={poll.options}
        total_vote_count={poll.total_vote_count} voteHandler={this.voteHandler}
        close_date={time_remaining} classContext={this.props.classContext} />
    );
  }.bind(this));

    return (
      <div>
        <h1 style={Align}>{this.props.header}</h1>
        <br />
        <div className="row">{polls}</div>
      </div>
    );
  }
});

var AllPolls = React.createClass({

  getInitialState: function(){
    return {polls: {'Polls': []}, header: '', classContext: ''};
  },

  loadPollsFromServer: function(){

    // pollName is available as a prop
    var pollName = this.props.routeParams.pollName

    if(pollName){
        var url = origin + '/api/poll/' + pollName
        this.setState({classContext: 'col-sm-6 col-sm-offset-3'})

    } else {
        var url = origin + '/api/polls'
        this.setState({header: 'Latest polls', classContext: 'col-sm-6'})
    }

    //make get request
    $.ajax({
      url: url,
      dataType: 'json',
      cache: false,
      success: function(data) {
        this.setState({polls: data});
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(url, status, err.toString());
      }.bind(this)
    });
  },

  componentDidMount: function(){
    this.loadPollsFromServer()
  },

  render: function(){

    // if a message was returned in the json result (the poll wasn't found)
    if(!this.state.polls.message){

    return (
      <LivePreviewProps polls={this.state.polls} loadPollsFromServer={this.loadPollsFromServer}
      header={this.state.header} classContext={this.state.classContext} />
      );
    } else {
      return (
          <div style={Align}>
            <h1>Poll not found</h1>
            <p>You might be interested in these <a href="/">polls</a></p>
          </div>
        )
      }
    }
  });

ReactDOM.render((
  <Router history={browserHistory}>
    <Route path="/" component={AllPolls} />
    <Route path="/polls" component={PollForm} />
    <Route path="/polls/:pollName" component={AllPolls} />
  </Router>
  ),
  document.getElementById('container')
);
