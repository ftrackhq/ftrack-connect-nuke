..
    :copyright: Copyright (c) 2015 ftrack

.. _release/migration:

***************
Migration notes
***************


Migrate to next
===============

Start/End Frame from environments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. _release/migration/next/start_end_frame_from_environments:

Previous to this release it was not possible to have the start frame ($FS) and end frame ($FE)
set from environments.

.. _release/migration/next/new_render_asset_type:

New render asset type
^^^^^^^^^^^^^^^^^^^^^

Previous to this release it was not possible to publish renders of other types
than image sequences. This has now been resolved and requires an :term:`asset type`
called `render`.

To enable this make sure that an :term:`asset type` with short code `render` is
available on your server.