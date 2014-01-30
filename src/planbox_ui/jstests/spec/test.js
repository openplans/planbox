/*global describe it beforeEach Planbox assert sinon*/

(function () {
  'use strict';
  describe('models.js', function () {

    it('should have a Planbox namespace', function () {
      assert.isDefined(Planbox);
    });

    describe('ProjectModel', function () {
      var p;

      beforeEach(function(done) {
        p = new Planbox.ProjectModel({label: 'My Project', events: []});
        done();
      });

      it('has an events collection', function() {
        assert.isDefined(p.get('events'));
      });

      describe('clean', function() {
        it('should get rid of empty events', function() {
          p.get('events').add([{label: 'Event 1'}, {}, {label: 'Event 3'}]);
          p.clean();
          assert.deepEqual(p.get('events').toJSON(), [{label: 'Event 1'}, {label: 'Event 3'}]);
        });
      });
    });

    describe('EventCollection', function () {
      var c;

      beforeEach(function(done){
        c = new Planbox.EventCollection([{id: 1}, {id: 2}, {id: 3}, {id: 4}, {id: 5}]);
        done();
      });

      it('should be defined', function () {
        assert.isDefined(Planbox.EventCollection);
      });

      it('should move it later in the list', function() {
        var m = c.at(0);
        c.moveTo(m, 2);
        assert.deepEqual(c.pluck('id'), [2, 3, 1, 4, 5]);
      });

      it('should move it earlier in the list', function() {
        var m = c.at(4);
        c.moveTo(m, 2);
        assert.deepEqual(c.pluck('id'), [1, 2, 5, 3, 4]);
      });

      it('should move it to the beginning', function() {
        var m = c.at(3);
        c.moveTo(m, 0);
        assert.deepEqual(c.pluck('id'), [4, 1, 2, 3, 5]);
      });

      it('should move it to the end', function() {
        var m = c.at(1);
        c.moveTo(m, 4);
        assert.deepEqual(c.pluck('id'), [1, 3, 4, 5, 2]);
      });

      it('should trigger a reorder event', function() {
        var onAdd = sinon.stub(),
            onRemove = sinon.stub(),
            onReorder = sinon.stub();

        c.on('add', onAdd);
        c.on('remove', onRemove);
        c.on('reorder', onReorder);

        var m = c.at(1);
        c.moveTo(m, 4);

        assert.equal(onAdd.callCount, 0);
        assert.equal(onRemove.callCount, 0);
        assert.equal(onReorder.callCount, 1);
      });

      it('should not trigger a reorder event when moving to the same spot', function() {
        var onAdd = sinon.stub(),
            onRemove = sinon.stub(),
            onReorder = sinon.stub();

        c.on('add', onAdd);
        c.on('remove', onRemove);
        c.on('reorder', onReorder);

        var m = c.at(1);
        c.moveTo(m, 1);

        assert.equal(onAdd.callCount, 0);
        assert.equal(onRemove.callCount, 0);
        assert.equal(onReorder.callCount, 0);
      });


    });
  });
}());
