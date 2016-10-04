// css style to align text to the center of it's container
var Align = {
  textAlign: 'center'
};

var PollForm = React.createClass({

  getInitialState: function(e){
    // set initial state of form inputs
    return {title: '', option: '', options: []}
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
    options: this.state.options.concat({name: this.state.option})
    });
    this.setState({option: ''});
  },

  handleSubmit: function(e){
    //TODO handle form submit
    e.preventDefault();
  },

  render: function(){
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
          <input type="text" id="option" name="option" className="form-control" placeholder="Option" onChange={this.handleOptionChange}  required autoFocus />
        </div>

        <div className="row form-group">
          <button className="btn btn-lg btn-success btn-block" onClick={this.handleOptionAdd}>Add option</button>
          <button className="btn btn-lg btn-success btn-block" type="submit">Save poll</button>
        </div>
        <br />
      </form>

      <h3 style={Align}>Live Preview</h3>
      <LivePreview title={this.state.title} options={this.state.options} />
    </div>
    );
  }
});

var LivePreview = React.createClass({
  render: function(){

    var options = this.props.options.map(function(option){

      if(option.name) {
        return (
          <div key={option.name}>
            <input name="options" type="radio" value={option.name} /> {option.name}
            <br />
          </div>
        );
      }
    });

    return(
      <div className="panel panel-success">
        <div className="panel-heading">
          <h4>{this.props.title}</h4>
        </div>
        <div className="panel-body">
          <form>
            {options}
            <br />
            <button type="submit" className="btn btn-success btn-outline hvr-grow">Vote!</button>
          </form>
        </div>
      </div>
    )
  }
});

ReactDOM.render(
  <div>
    <PollForm />
  </div>,
  document.getElementById('form_container')
);
