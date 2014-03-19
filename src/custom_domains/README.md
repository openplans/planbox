How we do custom domains
========================

We’ll be able to map domains to profile and project pages.

* customdomain.com → openplans.org/my-profile/
* customdomain.com → openplans.org/my-profile/my-project/

When we receive any request, in middleware we check first whether its domain is custom (i.e., unknown to us). If it is known (basically if it's openplans.org or www.openplans.org), we send Django on its merry way and process the request as normal.

If it is a custom domain (which may include things like my-profile.openplans.org as well as mycustomdomain.com), then our middleware searches for it among our known mappings. If and the middleware finds the domain, it modifies the request before sending it along:

* Sets `request.actual_path_info` to the current `request.path_info` value.
* Changes `request.path_info` to the root path in the mapping
* Sends the request along

At this point, Django's request handler will choose the appropriate view, passing in the appropriate arguments and so on. There are __ things we have to be careful of:

* django.core.urlresolvers.reverse will construct full paths, and not take the mapped root into account. Should we have a `request.reverse` that we should use instead, when appropriate?
* The `{% url %}` template tag won't notice the mapped root path either. Do we need to override the tag?
* The `STATIC_URL` template variable needs to be overwritten too.


Static Files and Media
----------------------

Certain projects will have images that were uploaded by the client. These should be on something like S3 and be referred to by absolute URLs anyway, so should not create any significant problems in practice. The static root URL WILL be tricky in these ways:

* The files will not be available at */static/*.  We'll have to know about the
  "proper" domain to use. Because of this, we should set a `CANONICAL_ROOT`
  environment variable. This domain should include the 


Caching
-------

If caching based on the request path, use the complete URL instead, with the different domain.
