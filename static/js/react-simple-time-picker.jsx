import React from 'react'
require('./style.css');

var DayPicker =  React.createClass({
  getInitialState: function(e){
    return {day: 0};
  },

  onChange: function(e){

    var difference = + e.target.value - this.state.day;
    var value = e.target.value;

    if(value >= 0 && value <= this.props.days){
      this.setState({day: value});

      this.props.updateDate({day: difference});
    }
  },

  render: function(e){
    return (
      <input type="number" name="day" required className="form-control time-picker"
      onChange={this.onChange} value={this.state.day} />
    )
  }
});

var HourPicker =  React.createClass({
  getInitialState: function(e){
    return {hour: 0};
  },

  onChange: function(e){

    var difference = + e.target.value - this.state.hour;
    var value = e.target.value;

    if(value >= 0 && value <= 23){
      this.setState({hour: value});

      this.props.updateDate({hour: difference});
    }
  },

  render: function(){
    return (
      <input type="number" name="hour" required className="form-control time-picker"
      onChange={this.onChange} value={this.state.hour} />
    )
  }
});

var MinutePicker =  React.createClass({
  getInitialState: function(e){
    return {minute: 0};
  },

  onChange: function(e){

    var difference = + e.target.value - this.state.minute;
    var value = e.target.value;

    if(value >= 0 && value <= 3000){
      this.setState({minute: value});

      this.props.updateDate({minute: difference});
    }
  },

  render: function(){

    return (
      <input type="number" name="minutes" required className="form-control time-picker"
      onChange={this.onChange} value={this.state.minute} />
    )
  }
});

var SimpleTimePicker = React.createClass({
    getInitialState: function(e){
      return {date: new Date()};
    },

    updateDate: function(date){

      var day = date.day;
      var hour = date.hour;
      var minute = date.minute;

      if(day) {
        this.onChange(day, 'day');
      }

      if(hour){
        this.onChange(hour, 'hour');
      }

      if(minute){
        this.onChange(minute, 'minute');
      }

    },

    onChange: function(num, time_var){

      var now = new Date(this.state.date.getTime());

      switch(time_var){
        case 'day':
          num += now.getDate();
          now.setDate(num);
          break;

        case 'hour':
          num += now.getHours();
          now.setHours(num);
          break;

        case 'minute':
          num += now.getMinutes();
          now.setMinutes(num);
          break;
      }

      this.setState({date: now});
      this.props.onChange(now);

    },

    render: function(){

      return (
        <div className="input-group" style={this.props.style}>
          <DayPicker days={this.props.days} updateDate={this.updateDate} />
          <small className="days">Days</small>

          <HourPicker updateDate={this.updateDate} />
          <small>Hours</small>

          <MinutePicker updateDate={this.updateDate} />
          <small>Mins</small>
      </div>
      )
    }
  });
  

export default SimpleTimePicker;
